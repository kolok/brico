from audits.views.audits import AuditDetailView, NewAuditView, delete_audit
from audits.views.comment import (
    CommentCreateView,
    CommentDeleteView,
    CommentFormCancelView,
    CommentFragmentView,
    CommentListView,
    CommentUpdateView,
)
from audits.views.criteria import CriterionDetailView
from audits.views.projects import ProjectDetailView, ProjectListView
from audits.views.prompt import PromptFormView
from audits.views.tests import (
    ChatView,
    ConversationListView,
    FooBarView,
    NewConversationView,
    SendMessageView,
)
from django.urls import path
from django.views.generic import TemplateView

app_name = "audits"

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    # FIXME : supprimer cette vue -> uniquement pour le test
    path("foobar/", FooBarView.as_view(), name="foobar"),
    # Chat URLs
    path("conversations/", ConversationListView.as_view(), name="chat_list"),
    path("chat/new/", NewConversationView.as_view(), name="new_conversation"),
    path("chat/<int:conversation_id>/", ChatView.as_view(), name="chat"),
    path(
        "chat/<int:conversation_id>/send/",
        SendMessageView.as_view(),
        name="send_message",
    ),
    # end FIXME
    # Projects URLs
    path("projects/", ProjectListView.as_view(), name="project_list"),
    path("projects/<slug:slug>/", ProjectDetailView.as_view(), name="project_detail"),
    # Audits URLs
    path(
        "projects/<str:project_slug>/audits/<int:pk>/",
        AuditDetailView.as_view(),
        name="audit_detail",
    ),
    path(
        "projects/<slug:project_slug>/audits/new/",
        NewAuditView.as_view(),
        name="new_audit",
    ),
    path(
        "projects/<str:project_slug>/audits/<int:pk>/delete/",
        delete_audit,
        name="audit_delete",
    ),
    # Criteria URLs
    path(
        "projects/<str:project_slug>/audits/<int:audit_id>/criteria/<int:pk>/",
        CriterionDetailView.as_view(),
        name="criterion_detail",
    ),
    # Comments URLs
    path(
        (
            "projects/<str:project_slug>/audits/<int:audit_id>/"
            "criteria/<int:criterion_id>/comments/"
        ),
        CommentListView.as_view(),
        name="comments_list",
    ),
    path(
        (
            "projects/<str:project_slug>/audits/<int:audit_id>/"
            "criteria/<int:criterion_id>/comments/new/"
        ),
        CommentCreateView.as_view(),
        name="comment_create",
    ),
    path(
        (
            "projects/<str:project_slug>/audits/<int:audit_id>/"
            "criteria/<int:criterion_id>/comments/<int:pk>/edit/"
        ),
        CommentUpdateView.as_view(),
        name="comment_update",
    ),
    path(
        (
            "projects/<str:project_slug>/audits/<int:audit_id>/"
            "criteria/<int:criterion_id>/comments/<int:pk>/delete/"
        ),
        CommentDeleteView.as_view(),
        name="comment_delete",
    ),
    path(
        (
            "projects/<str:project_slug>/audits/<int:audit_id>/"
            "criteria/<int:criterion_id>/comments/cancel/"
        ),
        CommentFormCancelView.as_view(),
        name="comment_form_cancel",
    ),
    path(
        (
            "projects/<str:project_slug>/audits/<int:audit_id>/"
            "criteria/<int:criterion_id>/comments/<int:pk>/fragment/"
        ),
        CommentFragmentView.as_view(),
        name="comment_fragment",
    ),
    # Prompts URLs
    path(
        (
            "projects/<str:project_slug>/audits/<int:audit_id>/"
            "criteria/<int:criterion_id>/prompts/"
        ),
        PromptFormView.as_view(),
        name="prompt",
    ),
]
