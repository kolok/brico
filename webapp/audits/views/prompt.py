import logging
import uuid
from pathlib import Path
from urllib.parse import urlencode

from audits.forms import PromptForm
from audits.models.audit import ProjectAuditCriterion, Prompt
from audits.views.mixin import CriteriaChildrenMixin
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as translate
from django.views.generic import FormView
from organization.mixins import OrganizationPermissionMixin
from pydantic_ai import Agent

logger = logging.getLogger(__name__)


def load_system_prompt(
    criterion_name: str,
    criterion_description: str,
    resources: str,
    language: str,
) -> str:
    prompt_path = Path(settings.BASE_DIR) / "audits" / "prompts" / "system_prompt.md"
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()
    return prompt_template.format(
        criterion_name=criterion_name,
        criterion_description=criterion_description,
        resources=resources,
        language=language,
    )


class PromptFormView(
    LoginRequiredMixin, CriteriaChildrenMixin, OrganizationPermissionMixin, FormView
):
    form_class = PromptForm
    model = Prompt
    template_name = "audits/prompt/detail.html"

    def _filter_prompt_in_error(self, messages_history: list[dict]) -> list[dict]:
        """Filter out error messages and user messages that precede them."""
        history_messages = []
        for i, msg in enumerate(messages_history):
            # Skip error messages
            if msg["role"] == "error":
                continue
            # Skip user messages that are immediately before an error message
            if (
                msg["role"] == "user"
                and i + 1 < len(messages_history)
                and messages_history[i + 1]["role"] == "error"
            ):
                continue
            # Include user and assistant messages
            if msg["role"] in ["user", "assistant"]:
                history_messages.append(msg)
        return history_messages

    def _get_queryset_with_organization_filter(
        self, queryset: QuerySet[Prompt]
    ) -> QuerySet[Prompt]:
        return queryset.prefetch_related(
            "project_audit_criterion__project_audit__project"
        ).filter(
            project_audit_criterion__project_audit__project__organization_id=self.current_organization_id
        )

    def _get_object_organization_id(self) -> int:
        """Get object organization ID."""
        if not hasattr(self, "get_object"):
            raise PermissionDenied("Object not found")
        obj = self.get_object()  # type: ignore[misc]
        if obj:
            project = obj.project_audit_criterion.project_audit.project
            return project.organization_id
        raise PermissionDenied("Object not found")

    def _get_criterion_filtered(self) -> ProjectAuditCriterion:
        """Get criterion filtered by organization."""
        criterion_id = self.kwargs.get("criterion_id")  # type: ignore[attr-defined]
        return get_object_or_404(
            ProjectAuditCriterion.objects.prefetch_related(
                "project_audit__project"
            ).filter(
                project_audit__project__organization_id=self.current_organization_id
            ),
            id=criterion_id,
        )

    def get_object(self):
        """Return None for FormView, but ensure criterion is filtered."""
        # This method is called by the mixin's dispatch to check permissions
        # For FormView, we need to verify the criterion belongs to the organization
        self._get_criterion_filtered()
        return None  # FormView doesn't have an object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        criterion = self._get_criterion_filtered()
        context["criterion"] = criterion
        context["audit"] = criterion.project_audit
        context["project"] = criterion.project_audit.project
        # Use the form's session_id if it exists, otherwise generate a new one
        session_id = self.request.GET.get("session_id")
        if session_id:
            try:
                context["session_id"] = uuid.UUID(session_id)
                # Filter prompt by organization
                prompt_queryset = Prompt.objects.filter(
                    session_id=session_id, project_audit_criterion=criterion
                )
                prompt = get_object_or_404(
                    self._get_queryset_with_organization_filter(prompt_queryset)
                )
                context["prompt"] = prompt
            except (ValueError, TypeError):
                context["session_id"] = uuid.uuid4()
        else:
            context["session_id"] = uuid.uuid4()
        return context

    def get_initial(self):
        initial = super().get_initial()
        session_id = self.request.GET.get("session_id")
        if session_id:
            try:
                initial["session_id"] = uuid.UUID(session_id)

            except (ValueError, TypeError):
                pass
        return initial

    def get_success_url(self):
        # Get the session_id from the validated form
        session_id = getattr(self, "_session_id", None)
        criterion = self._get_criterion_filtered()

        url = reverse(
            "audits:prompt",
            kwargs={
                "project_slug": criterion.project_audit.project.slug,
                "audit_id": criterion.project_audit.id,
                "criterion_id": criterion.id,
            },
        )

        # Add the session_id as a query parameter
        if session_id:

            params = urlencode({"session_id": str(session_id)})
            return f"{url}?{params}"

        return url

    def form_valid(self, form):
        session_id = form.cleaned_data.get("session_id")
        # Store the session_id to use it in get_success_url
        self._session_id = session_id

        user_message = form.cleaned_data.get("message", "").strip()
        name = user_message if user_message else translate("Prompt without question")
        max_name_length = Prompt._meta.get_field("name").max_length
        if len(name) > max_name_length:
            name = name[: max_name_length - 1] + "…"

        if user_message == "":
            user_message = (
                "can you check this assertion and tell me it is compliant, "
                "not compliant, partially compliant or not applicable?"
            )

        criterion = self._get_criterion_filtered()
        prompt, _ = Prompt.objects.get_or_create(
            session_id=session_id,
            project_audit_criterion=criterion,
            defaults={"name": name},
        )

        messages_history = prompt.prompt.get("messages", [])
        # Filter out error messages and user messages that precede them
        filtered_messages_history = self._filter_prompt_in_error(messages_history)

        if not hasattr(settings, "ANTHROPIC_API_KEY") or not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")
        project = criterion.project_audit.project
        resources = ""
        for resource in project.resources.all():
            resources += f"- {resource.get_type_display()}: {resource.url}\n"
        system_prompt = load_system_prompt(
            criterion_name=criterion.criterion.name,
            criterion_description=criterion.criterion.description,
            resources=resources,
            language="english",
        )

        agent = Agent(
            settings.ANTHROPIC_MODEL,
            instructions=system_prompt,
        )

        try:
            # Send the message to Claude with the history
            result = agent.run_sync(
                user_message,
                message_history=(
                    filtered_messages_history if filtered_messages_history else None
                ),  # type: ignore
            )

            messages_history.extend(
                [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": result.output},
                ]
            )

            # Save the updated history to the JSON prompt

        except Exception as err:
            # In case of error, continue anyway to not block the user
            # The error could be logged here if necessary
            logger.error("Something goes wrong: %s", err, exc_info=True)
            error_message = f"""
## An error occurred:

{str(err)}

            """
            messages_history.extend(
                [
                    {"role": "user", "content": user_message},
                    {"role": "error", "content": error_message},
                ]
            )
        finally:
            prompt.prompt = {"messages": messages_history}
            prompt.save()

        return super().form_valid(form)
