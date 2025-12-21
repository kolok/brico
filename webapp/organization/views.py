"""
Views for organization management.
"""

from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY, ORGANIZATIONS_SESSION_KEY
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db import transaction
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy
from django.views.generic import CreateView, RedirectView
from organization.models import Organization, OrganizationMember


class OrganizationCreateView(LoginRequiredMixin, CreateView):
    """View to create a new organization."""

    model = Organization
    fields = ["name", "description"]
    template_name = "organization/organization_create.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        """Associate the created organization to the user and set it as current."""
        with transaction.atomic():
            # Créer l'organisation
            organization = form.save()

            # Check if it is the first organization of the user
            is_first_org = not OrganizationMember.objects.filter(
                user=self.request.user
            ).exists()

            # Create relationship with the user
            # Creator gets administrator role

            admin_group, _ = Group.objects.get_or_create(name="administrator")
            OrganizationMember.objects.create(
                user=self.request.user,
                organization=organization,
                group=admin_group,
                is_default=is_first_org,
            )

            # Set this organization as current in the session
            self.request.session[CURRENT_ORGANIZATION_SESSION_KEY] = (
                organization.id,
                organization.name,
            )
            # Will force to compute again the organizations in the session
            self.request.session.pop(ORGANIZATIONS_SESSION_KEY)

        messages.success(
            self.request,
            gettext_lazy(
                'Organization "{organization_name}" created successfully.'
            ).format(organization_name=organization.name),
        )
        return super().form_valid(form)


class OrganizationSwitchView(LoginRequiredMixin, RedirectView):
    """View to change the current organization."""

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """Change the current organization in the session."""
        from django.urls import reverse

        organization_id = kwargs.get("organization_id")

        if organization_id:
            # Check if the user has access to this organization
            # TODO: check if we can manage it with permissions
            try:
                organization = Organization.objects.get(
                    id=organization_id,
                    memberships__user=self.request.user,
                )
                # Update session
                self.request.session[CURRENT_ORGANIZATION_SESSION_KEY] = (
                    organization.id,
                    organization.name,
                )

                messages.success(
                    self.request,
                    gettext_lazy('Organization "{organization_name}" selected.').format(
                        organization_name=organization.name
                    ),
                )
            except Organization.DoesNotExist:
                # TODO: check if we can manage it with permissions
                messages.error(
                    self.request,
                    gettext_lazy("You do not have access to this organization."),
                )

        return reverse("dashboard")
