from audits.views import (
    AuditDetailView,
    ChatView,
    ConversationListView,
    FooBarView,
    NewAuditView,
    NewConversationView,
    ProjectDetailView,
    ProjectListView,
    SendMessageView,
    delete_audit,
)
from django.urls import path
from django.views.generic import TemplateView

app_name = "audits"

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
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
    path("projects/", ProjectListView.as_view(), name="project_list"),
    path("projects/<slug:slug>/", ProjectDetailView.as_view(), name="project_detail"),
    path(
        "projects/audits/<int:pk>/",
        AuditDetailView.as_view(),
        name="audit_detail",
    ),
    path(
        "projects/<int:project_id>/audits/new/",
        NewAuditView.as_view(),
        name="new_audit",
    ),
    path(
        "projects/audits/<int:pk>/delete/",
        delete_audit,
        name="audit_delete",
    ),
]
