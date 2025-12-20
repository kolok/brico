import logging
import uuid
from pathlib import Path

from audits.forms import PromptForm
from audits.models.audit import Prompt
from audits.views.mixin import CriteriaChildrenMixin
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse
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
    template_name = "audits/prompt.html"

    def _get_queryset_with_organization_filter(
        self, queryset: QuerySet[Prompt]
    ) -> QuerySet[Prompt]:
        return queryset.prefetch_related(
            "project_audit_criterion__project_audit__project"
        ).filter(
            project_audit_criterion__project_audit__project__organization_id=self.current_organization_id
        )

    def _get_object_organization_id(self) -> int:
        return (
            self.get_object().project_audit_criterion.project_audit.project.organization_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["criterion"] = self._get_criterion()
        context["audit"] = self._get_audit()
        context["project"] = self._get_project()
        # Use the form's session_id if it exists, otherwise generate a new one
        session_id = self.request.GET.get("session_id")
        if session_id:
            try:
                context["session_id"] = uuid.UUID(session_id)
                prompt = Prompt.objects.get(session_id=session_id)
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

        url = reverse(
            "audits:prompt",
            kwargs={
                "project_slug": self._get_project().slug,
                "audit_id": self._get_audit().id,
                "criterion_id": self._get_criterion().id,
            },
        )

        # Add the session_id as a query parameter
        if session_id:
            from urllib.parse import urlencode

            params = urlencode({"session_id": str(session_id)})
            return f"{url}?{params}"

        return url

    def form_valid(self, form):
        session_id = form.cleaned_data.get("session_id")
        # Store the session_id to use it in get_success_url
        self._session_id = session_id

        message = form.cleaned_data.get("message", "").strip()
        name = message if message else "Prompt"
        max_name_length = Prompt._meta.get_field("name").max_length
        if len(name) > max_name_length:
            name = name[: max_name_length - 1] + "…"

        prompt, _ = Prompt.objects.get_or_create(
            session_id=session_id,
            project_audit_criterion=self._get_criterion(),
            defaults={"name": name},
        )

        user_message = form.cleaned_data.get("message", "").strip()
        if not user_message:
            return super().form_valid(form)
        criterion = self._get_criterion()
        messages_history = prompt.prompt.get("messages", [])
        history_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in messages_history
        ]
        if not hasattr(settings, "ANTHROPIC_API_KEY") or not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")
        project = self._get_project()
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
                message_history=history_messages if history_messages else None,  # type: ignore
            )

            messages_history.extend(
                [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": result.output},
                ]
            )

            # Save the updated history to the JSON prompt
            prompt.prompt = {"messages": messages_history}
            prompt.save()

        except Exception as err:
            # In case of error, continue anyway to not block the user
            # The error could be logged here if necessary
            logger.error("Something goes wrong: %s", err, exc_info=True)

        return super().form_valid(form)
