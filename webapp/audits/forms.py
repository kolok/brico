from audits.models.audit import AuditLibrary, Criterion
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
