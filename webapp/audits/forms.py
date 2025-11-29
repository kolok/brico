import uuid

from audits.models.audit import AuditLibrary, ProjectAuditCriterionComment
from django import forms


class NewAuditForm(forms.Form):
    audit_library = forms.ModelChoiceField(queryset=AuditLibrary.objects.all())


class CommentForm(forms.ModelForm):
    class Meta:
        model = ProjectAuditCriterionComment
        fields = ["comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Add a comment...",
                    "class": (
                        "w-full px-3 py-2 border border-gray-300 rounded-md"
                        " focus:outline-none focus:ring-2 focus:ring-blue-500"
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
