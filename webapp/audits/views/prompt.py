import uuid

from audits.forms import PromptForm
from audits.models.audit import (
    ProjectAudit,
    ProjectAuditCriterion,
    ProjectAuditCriterionPrompt,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import FormView
from organization.models.organization import Project
from pydantic_ai import Agent


class PromptParentMixin(View):
    def _get_criterion(self):
        criterion_id = self.kwargs.get("criterion_id")
        return get_object_or_404(ProjectAuditCriterion, id=criterion_id)

    def _get_audit(self):
        audit_id = self.kwargs.get("audit_id")
        return get_object_or_404(ProjectAudit, id=audit_id)

    def _get_project(self):
        project_slug = self.kwargs.get("project_slug")
        return get_object_or_404(Project, slug=project_slug)


class PromptFormView(LoginRequiredMixin, PromptParentMixin, FormView):
    """API pour envoyer un message à l'IA et recevoir une réponse."""

    form_class = PromptForm
    template_name = "audits/prompt.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["criterion"] = self._get_criterion()
        context["audit"] = self._get_audit()
        context["project"] = self._get_project()
        # Utiliser le session_id du formulaire s'il existe, sinon en générer un nouveau
        session_id = self.request.GET.get("session_id")
        if session_id:
            try:
                context["session_id"] = uuid.UUID(session_id)
                prompt = ProjectAuditCriterionPrompt.objects.get(session_id=session_id)
                context["prompt"] = prompt
            except (ValueError, TypeError):
                context["session_id"] = uuid.uuid4()
        else:
            context["session_id"] = uuid.uuid4()
        return context

    def get_initial(self):
        """Initialise le formulaire avec le session_id de la query string si présent."""
        initial = super().get_initial()
        session_id = self.request.GET.get("session_id")
        if session_id:
            try:
                initial["session_id"] = uuid.UUID(session_id)

            except (ValueError, TypeError):
                pass
        return initial

    def get_success_url(self):
        # Récupérer le session_id depuis le formulaire validé
        session_id = getattr(self, "_session_id", None)

        url = reverse(
            "audits:prompt",
            kwargs={
                "project_slug": self._get_project().slug,
                "audit_id": self._get_audit().id,
                "criterion_id": self._get_criterion().id,
            },
        )

        # Ajouter le session_id comme paramètre de requête
        if session_id:
            from urllib.parse import urlencode

            params = urlencode({"session_id": str(session_id)})
            return f"{url}?{params}"

        return url

    def form_valid(self, form):
        session_id = form.cleaned_data.get("session_id")
        # Stocker le session_id pour l'utiliser dans get_success_url
        self._session_id = session_id

        message = form.cleaned_data.get("message", "").strip()
        name = message if message else "Prompt"
        if len(name) > 255:
            name = name[:254] + "…"

        prompt, _ = ProjectAuditCriterionPrompt.objects.get_or_create(
            session_id=session_id,
            project_audit_criterion=self._get_criterion(),
            defaults={"name": name},
        )

        # Récupérer le message de l'utilisateur
        user_message = form.cleaned_data.get("message", "").strip()
        if not user_message:
            return super().form_valid(form)

        # Récupérer le critère pour le contexte
        criterion = self._get_criterion()

        # Récupérer l'historique des messages depuis le prompt JSON
        messages_history = prompt.prompt.get("messages", [])

        # Préparer l'historique pour pydantic_ai
        history_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in messages_history
        ]

        # Créer l'agent avec des instructions spécifiques au contexte d'audit
        agent = Agent(
            "anthropic:claude-sonnet-4-0",
            instructions=(
                "Tu es un assistant expert en audit et conformité. "
                f"Tu aides à analyser le critère suivant : {criterion.criterion.name}. "
                f"Description : {criterion.criterion.description}. "
                "Réponds de manière claire, précise et professionnelle. "
                "Utilise le markdown pour formater tes réponses si nécessaire. "
                "L'utilisateur qui pose les question doit répondre si le critère est"
                " conforme, partiellement conforme ou non conforme. "
                "répond en anglais. "
                "Le code de l'application à analysé est disponible à l'url suivante: "
                "https://github.com/MTES-MCT/apilos/"
            ),
        )

        try:
            # Envoyer le message à Claude avec l'historique
            result = agent.run_sync(
                user_message,
                message_history=history_messages if history_messages else None,  # type: ignore
            )

            # Ajouter le message utilisateur et la réponse à l'historique
            messages_history.append(
                {
                    "role": "user",
                    "content": user_message,
                }
            )
            messages_history.append(
                {
                    "role": "assistant",
                    "content": result.output,
                }
            )

            # Sauvegarder l'historique mis à jour dans le prompt JSON
            prompt.prompt = {"messages": messages_history}
            prompt.save()

        except Exception:
            # En cas d'erreur, on continue quand même pour ne pas bloquer l'utilisateur
            # L'erreur pourrait être loggée ici si nécessaire
            pass

        return super().form_valid(form)
