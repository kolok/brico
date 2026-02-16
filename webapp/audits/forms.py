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
    """
    Accept tag names via TagsWidget and resolve them to Tag instances.

    Unlike ModelMultipleChoiceField, this field does not reject values
    missing from the queryset: it creates new Tags on the fly (scoped to
    the organization set on the field).  ``cleaned_data['tags']`` therefore
    contains a list of ``Tag`` objects, exactly like
    ``ModelMultipleChoiceField`` would.
    """

    widget = TagsWidget

    def __init__(self, *args, **kwargs) -> None:
        self.organization: Organization | None = None
        super().__init__(*args, **kwargs)

    def clean(self, value: list[str] | str | None) -> list[Tag]:
        """Resolve tag names to Tag instances, creating missing ones."""
        if not value:
            return []
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            raise forms.ValidationError("Invalid tags format.")

        tags: list[Tag] = []
        for item in value:
            if not isinstance(item, str):
                continue
            name = item.strip()
            if not name:
                continue
            slug = slugify(name)
            if self.organization is not None:
                tag, _ = Tag.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "organization": self.organization,
                    },
                )
            else:
                try:
                    tag = Tag.objects.get(slug=slug)
                except Tag.DoesNotExist:
                    raise forms.ValidationError(
                        'Tag "%(name)s" does not exist.', params={"name": name}
                    )
            tags.append(tag)
        return tags


class AuditLibraryForm(forms.ModelForm):
    """
    Form used in organization settings to edit an AuditLibrary with tags.

    Tags are managed through a custom widget. The widget keeps a list of hidden
    inputs (one per tag) in sync with the selected tag names.

    ``cleaned_data['tags']`` is a list of ``Tag`` objects (like
    ``ModelMultipleChoiceField``).  Django's ``_save_m2m`` takes care of
    persisting the relationship when ``save(commit=True)`` is called.
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

        Populates the TagsWidget choices from the instance's current tags
        so the Stimulus controller can render them on initial page load.
        """
        self.organization: Organization | None = organization
        super().__init__(*args, **kwargs)

        # Let the field know which organization to scope new tags to.
        resolved_org = organization or (
            self.instance.organization if self.instance and self.instance.pk else None
        )
        self.fields["tags"].organization = resolved_org  # type: ignore[union-attr]


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
