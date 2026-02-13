import uuid

from audits.models.audit import (
    AuditLibrary,
    AuditLibraryTag,
    Comment,
    ProjectAuditCriterion,
)
from django import forms
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from organization.models.organization import Organization, Project, Resource


class AuditLibraryTagsWidget(forms.Widget):
    """
    Custom widget used to manage AuditLibrary tags with a tag input UI.
    """

    template_name = "components/audit_library_tags_widget.html"

    # def value_from_datadict(self, data, files, name):
    #     """
    #     Extract all tag values from the POST data.

    #     The widget renders one hidden input per tag, all sharing the same name,
    #     so we must use ``getlist()`` to retrieve them.
    #     """
    #     try:
    #         # Django's QueryDict exposes ``getlist``, but type checkers only see
    #         # a generic mapping here, so we guard the call defensively.
    #         getlist = data.getlist  # type: ignore[attr-defined]
    #     except AttributeError:  # pragma: no cover - safety net for non-QueryDict
    #         value = data.get(name, [])
    #         if isinstance(value, list):
    #             return value
    #         if value:
    #             return [value]
    #         return []
    #     else:
    #         return getlist(name)

    # def render(self, name, value, attrs=None, renderer=None):
    #     attrs = attrs or {}
    #     # Determine the DOM id for the hidden input
    #     input_id = attrs.get("id", f"id_{name}")

    #     # Prepare the initial list of tags from the stored JSON string, if any
    #     initial_tags: list[str] = []
    #     if value:
    #         try:
    #             decoded = json.loads(value) if isinstance(value, str) else value
    #             if isinstance(decoded, list):
    #               initial_tags = [str(item) for item in decoded if str(item).strip()]
    #         except json.JSONDecodeError:
    #             initial_tags = []

    #     hidden_value = json.dumps(initial_tags)

    #     html = render_to_string(
    #         "components/audit_library_tags_widget.html",
    #         {
    #             "name": name,
    #             "input_id": input_id,
    #             "hidden_value": hidden_value,
    #         },
    #     )
    #     return mark_safe(html)


class NewAuditForm(forms.Form):
    audit_library = forms.ModelChoiceField(queryset=AuditLibrary.objects.all())


class AuditLibraryForm(forms.ModelForm):
    """
    Form used in organization settings to edit an AuditLibrary with tags.

    Tags are managed through a custom widget. The widget keeps a list of hidden
    inputs (one per tag) in sync with the selected tag names.
    """

    audit_library_tags = forms.ModelMultipleChoiceField(
        queryset=AuditLibraryTag.objects.all(),
        required=False,
        widget=AuditLibraryTagsWidget(),
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=AuditLibraryTag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = AuditLibrary
        fields = ["name", "description", "audit_library_tags"]

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

    def clean_audit_library_tags(self) -> list[str]:
        """
        Clean the list of tag names coming from the widget.
        """
        raw_value = self.cleaned_data.get("audit_library_tags", [])
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

        tag_names: list[str] = self.cleaned_data.get("audit_library_tags", [])
        organization = self.organization or instance.organization

        tags: list[AuditLibraryTag] = []
        if tag_names and organization is not None:
            for name in tag_names:
                slug = slugify(name)
                tag, _ = AuditLibraryTag.objects.get_or_create(
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
