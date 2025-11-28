import uuid

from audits.models.audit import AuditLibrary, Criterion, ProjectAuditCriterionComment
from django import forms
from organization.models.organization import Organization


class FooBarForm(forms.Form):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        widget=forms.Select(
            attrs={
                "data-choose-criterion-target": "organization",
                "data-action": "change->choose-criterion#getChooseCriterion",
            }
        ),
    )
    audit_library = forms.ModelChoiceField(queryset=AuditLibrary.objects.all())
    criterion = forms.ModelChoiceField(queryset=Criterion.objects.all(), required=False)
    question = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 4, "placeholder": "Posez votre question à Claude..."}
        ),
        required=False,
        label="Question pour Claude",
        help_text="Envoyez une instruction ou une question à Claude pour analyse",
    )


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
                    "placeholder": "Ajoutez un commentaire...",
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
