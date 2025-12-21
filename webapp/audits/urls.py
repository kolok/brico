from audits.views.comment import (
    CommentCreateView,
    CommentDeleteView,
    CommentFormCancelView,
    CommentFragmentView,
    CommentListView,
    CommentUpdateView,
)
from audits.views.project import ProjectDetailView, ProjectFormView, ProjectListView
from audits.views.projectaudit import (
    DeleteProjectAuditView,
    NewProjectAuditView,
    ProjectAuditDetailView,
)
from audits.views.projectauditcriterion import CriterionDetailView
from audits.views.prompt import PromptFormView
from django.urls import path

app_name = "audits"

urlpatterns = [
    # Projects URLs
    path("project/", ProjectListView.as_view(), name="project_list"),
    path("project/new/", ProjectFormView.as_view(), name="project_form"),
    path("project/<slug:slug>/", ProjectDetailView.as_view(), name="project_detail"),
    # ProjectAudits URLs
    path(
        "project/<str:project_slug>/audit/<int:pk>/",
        ProjectAuditDetailView.as_view(),
        name="projectaudit_detail",
    ),
    path(
        "project/<slug:project_slug>/audit/new/",
        NewProjectAuditView.as_view(),
        name="projectaudit_new",
    ),
    path(
        "project/<str:project_slug>/audit/<int:pk>/delete/",
        DeleteProjectAuditView.as_view(),
        name="projectaudit_delete",
    ),
    # Criteria URLs
    path(
        "project/<str:project_slug>/audit/<int:audit_id>/criterion/<int:pk>/",
        CriterionDetailView.as_view(),
        name="projectauditcriterion_detail",
    ),
    # Comments URLs
    path(
        (
            "project/<str:project_slug>/audit/<int:audit_id>/"
            "criterion/<int:criterion_id>/comments/"
        ),
        CommentListView.as_view(),
        name="comments_list",
    ),
    path(
        (
            "project/<str:project_slug>/audit/<int:audit_id>/"
            "criterion/<int:criterion_id>/comments/new/"
        ),
        CommentCreateView.as_view(),
        name="comment_create",
    ),
    path(
        (
            "project/<str:project_slug>/audit/<int:audit_id>/"
            "criterion/<int:criterion_id>/comments/<int:pk>/edit/"
        ),
        CommentUpdateView.as_view(),
        name="comment_update",
    ),
    path(
        (
            "project/<str:project_slug>/audit/<int:audit_id>/"
            "criterion/<int:criterion_id>/comments/<int:pk>/delete/"
        ),
        CommentDeleteView.as_view(),
        name="comment_delete",
    ),
    path(
        (
            "project/<str:project_slug>/audit/<int:audit_id>/"
            "criterion/<int:criterion_id>/comments/cancel/"
        ),
        CommentFormCancelView.as_view(),
        name="comment_form_cancel",
    ),
    path(
        (
            "project/<str:project_slug>/audit/<int:audit_id>/"
            "criterion/<int:criterion_id>/comments/<int:pk>/fragment/"
        ),
        CommentFragmentView.as_view(),
        name="comment_fragment",
    ),
    # Prompts URLs
    path(
        (
            "project/<str:project_slug>/audit/<int:audit_id>/"
            "criterion/<int:criterion_id>/prompts/"
        ),
        PromptFormView.as_view(),
        name="prompt",
    ),
]
