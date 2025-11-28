# Create your views here.

# Criteria views
import json

from audits.forms import FooBarForm
from audits.models.chat import Conversation, Message
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView
from pydantic_ai import Agent


class FooBarView(FormView):
    template_name = "audits/foobar.html"
    form_class = FooBarForm
    success_url = reverse_lazy("audits:foobar")

    def form_valid(self, form):
        question = form.cleaned_data.get("question")

        if question:
            # Créer un agent pydantic_ai pour traiter la question
            agent = Agent(
                "anthropic:claude-sonnet-4-0",
                instructions=(
                    "Tu es un assistant expert en audit et conformité."
                    " Réponds de manière claire et concise.",
                ),
            )

            try:
                # Envoyer la question à Claude
                result = agent.run_sync(question)

                # Afficher la réponse de Claude
                messages.info(
                    self.request,
                    f"Réponse de Claude : {result.output}",
                    extra_tags="claude-response",
                )
            except Exception as e:
                messages.error(
                    self.request,
                    f"Erreur lors de la communication avec Claude : {str(e)}",
                )

        messages.success(self.request, _("Form submitted successfully"))
        return super().form_valid(form)


# Chat Views
class ConversationListView(LoginRequiredMixin, ListView):
    """Liste toutes les conversations de l'utilisateur."""

    model = Conversation
    template_name = "audits/chat_list.html"
    context_object_name = "conversations"
    paginate_by = 20

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).prefetch_related(
            "messages"
        )


class ChatView(LoginRequiredMixin, TemplateView):
    """Vue principale du chat avec Claude."""

    template_name = "audits/chat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversation_id = self.kwargs.get("conversation_id")

        if conversation_id:
            conversation = get_object_or_404(
                Conversation, id=conversation_id, user=self.request.user
            )
        else:
            # Créer une nouvelle conversation
            conversation = Conversation.objects.create(user=self.request.user)

        context["conversation"] = conversation
        context["messages"] = conversation.messages.all()
        return context


class SendMessageView(LoginRequiredMixin, View):
    """API pour envoyer un message et recevoir une réponse de Claude."""

    def post(self, request, conversation_id):
        try:
            # Récupérer la conversation
            conversation = get_object_or_404(
                Conversation, id=conversation_id, user=request.user
            )

            # Récupérer le contenu du message
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse(
                    {"error": "Le message ne peut pas être vide"}, status=400
                )

            # Sauvegarder le message de l'utilisateur
            Message.objects.create(
                conversation=conversation, role="user", content=user_message
            )

            # Récupérer l'historique complet de la conversation
            messages_history = conversation.messages.all()

            # Préparer l'historique pour pydantic_ai
            # pydantic_ai attend un format spécifique pour l'historique
            history_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages_history[
                    :-1
                ]  # Exclure le dernier message qu'on vient d'ajouter
            ]

            # Créer l'agent avec des instructions
            agent = Agent(
                "anthropic:claude-sonnet-4-0",
                instructions=(
                    "Tu es Claude, un assistant IA expert et polyvalent. "
                    "Tu es particulièrement compétent en audit, conformité,"
                    " développement logiciel et analyse. "
                    "Réponds de manière claire, précise et professionnelle. "
                    "Utilise le markdown pour formater tes réponses si nécessaire."
                ),
            )

            # Envoyer le message à Claude avec l'historique
            result = agent.run_sync(
                user_message,
                message_history=history_messages if history_messages else None,
            )

            # Sauvegarder la réponse de Claude
            assistant_message = Message.objects.create(
                conversation=conversation,
                role="assistant",
                content=result.output,
            )

            # Mettre à jour le titre de la conversation si c'est le premier message
            if conversation.messages.count() == 2:  # Premier échange
                # Générer un titre basé sur le premier message
                title_prompt = (
                    "Génère un titre court (max 50 caractères) pour une"
                    f" conversation qui commence par: {user_message[:100]}"
                )
                title_result = agent.run_sync(title_prompt)
                conversation.title = title_result.output[:255]
                conversation.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": {
                        "id": assistant_message.id,
                        "role": "assistant",
                        "content": assistant_message.content,
                        "created": assistant_message.created.isoformat(),
                    },
                    "conversation_title": conversation.title,
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class NewConversationView(LoginRequiredMixin, View):
    """Crée une nouvelle conversation et redirige vers le chat."""

    def get(self, request):
        conversation = Conversation.objects.create(user=request.user)
        return redirect("audits:chat", conversation_id=conversation.id)
