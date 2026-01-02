import uuid

from audits.models.audit import AuditLibrary, Comment
from django import forms
from organization.models.organization import Project


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
                    "placeholder": "Add a comment...",
                    "class": (
                        "w-full px-3 py-2 border border-gray-300 rounded-md"
                        " focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                    ),
                }
            ),
        }
        labels = {
            "comment": "",
        }


class PromptForm(forms.Form):
    message = forms.CharField(required=True)
    session_id = forms.UUIDField(widget=forms.HiddenInput(), initial=uuid.uuid4())


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]
        labels = {
            "name": "",
            "description": "",
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        from organization.models.organization import Resource

        model = Resource
        fields = ["name", "type", "url", "description"]
        widgets = {
            "url": forms.URLInput(
                attrs={
                    "class": "w-full max-w-[600px]",
                    "placeholder": "https://example.com",
                }
            ),
        }
