import uuid

from audits.models.audit import AuditLibrary, Comment, ProjectAuditCriterion
from django import forms
from django.utils.translation import gettext_lazy as _
from organization.models.organization import Project, Resource


class NewAuditForm(forms.Form):
    audit_library = forms.ModelChoiceField(queryset=AuditLibrary.objects.all())


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": _("Add a comment…"),
                    "class": "w-full",
                }
            ),
        }


class PromptForm(forms.Form):
    message = forms.CharField(
        label="",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "w-full",
                "rows": 2,
                "placeholder": _(
                    "Ask a question or leave it empty to get a general answer about"
                    " this criterion…"
                ),
            }
        ),
    )
    session_id = forms.UUIDField(widget=forms.HiddenInput(), initial=uuid.uuid4())


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ["name", "type", "url", "description"]
        widgets = {
            "url": forms.URLInput(
                attrs={
                    "class": "w-full max-w-[600px]",
                    "placeholder": "https://github.com/organization/repository",
                }
            ),
        }


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = ProjectAuditCriterion
        fields = ["status"]

    def clean_status(self):
        status = self.cleaned_data.get("status")
        if status not in ProjectAuditCriterion.ProjectAuditCriterionStatus.values:
            raise forms.ValidationError(_("Invalid status"))
        return status
