import logging
import uuid

from audits.models.audit import AuditLibrary, Comment, ProjectAuditCriterion, Tag
from django import forms
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from organization.models.organization import Organization, Project, Resource


class TagsWidget(forms.CheckboxSelectMultiple):
    """
    Custom widget used to manage tags with a tag input UI.
    """

    template_name = "components/input_tags.html"
    # FIXME : option_template_name = "components/input_tags_options.html"


class NewAuditForm(forms.Form):
    audit_library = forms.ModelChoiceField(queryset=AuditLibrary.objects.all())


class TagListField(forms.ModelMultipleChoiceField):
    widget = TagsWidget()


class AuditLibraryForm(forms.ModelForm):
    """
    Form used in organization settings to edit an AuditLibrary with tags.

    Tags are managed through a custom widget. The widget keeps a list of hidden
    inputs (one per tag) in sync with the selected tag names.
    """

    tags = TagListField(
        queryset=Tag.objects.all(),
        to_field_name="slug",
        required=False,
    )

    class Meta:
        model = AuditLibrary
        fields = ["name", "description", "tags"]

    def __init__(
        self,
        *args,
        organization: Organization | None = None,
        **kwargs,
    ) -> None:
        """
        Accept an optional organization to scope tag operations.
        """
        self.organization: Organization | None = organization
        super().__init__(*args, **kwargs)

    def clean_tags(self) -> list[str]:
        """
        Clean the list of tag names coming from the widget.
        """
        raw_value = self.cleaned_data.get("tags", [])
        if not raw_value:
            return []

        if not isinstance(raw_value, list):
            raise forms.ValidationError(_("Invalid tags format."))

        cleaned: list[str] = []
        for item in raw_value:
            if not isinstance(item, str):
                continue
            name = item.strip()
            if name:
                cleaned.append(name)

        return cleaned

    def save(self, commit: bool = True) -> AuditLibrary:
        """
        Save the AuditLibrary and synchronize its tags.

        Tags are created or retrieved by slug, which is generated from the tag
        name, and scoped to the provided organization when possible.
        """
        instance: AuditLibrary = super().save(commit=commit)

        tag_names: list[str] = self.cleaned_data.get("tags", [])
        logging.warning(f"self.cleaned_data: {self.cleaned_data}")

        organization = self.organization or instance.organization

        tags: list[Tag] = []
        if tag_names and organization is not None:
            for name in tag_names:
                slug = slugify(name)
                tag, _ = Tag.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "organization": organization,
                    },
                )
                tags.append(tag)

        if commit:
            # If no organization is available, we leave existing tags unchanged.
            if organization is not None:
                instance.tags.set(tags)

        return instance


class SearchForm(forms.Form):
    search = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Search by project name…"),
            }
        ),
    )


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
