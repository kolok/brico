"""
Custom Middleware
"""

from organization.models import OrganizationMember

CURRENT_ORGANIZATION_SESSION_KEY = "current_organization"
ORGANIZATIONS_SESSION_KEY = "user_organizations"


class ActiveNavMiddleware:
    """
    Middleware to determine which navigation links should have the 'active' class
    based on the request path.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        active_nav = {}

        if request.path.startswith("/audits/projects"):
            active_nav["projects"] = True
        if request.path.startswith("/dashboard"):
            active_nav["dashboard"] = True

        request.active_nav = active_nav

        response = self.get_response(request)
        return response


class OrganizationMiddleware:
    """
    Middleware pour gérer l'organisation courante de l'utilisateur en session.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        memberships = None

        if request.user.is_authenticated:
            # Manage user organizations
            if not request.session.get(ORGANIZATIONS_SESSION_KEY, []):
                # Get all organizations of the user
                memberships = OrganizationMember.objects.filter(
                    user=request.user
                ).select_related("organization")

                # Store user organizations in session
                request.session[ORGANIZATIONS_SESSION_KEY] = [
                    (membership.organization.id, membership.organization.name)
                    for membership in memberships
                ]

            # Manage current organization from request
            if request.session.get(
                ORGANIZATIONS_SESSION_KEY
            ) and not request.session.get(CURRENT_ORGANIZATION_SESSION_KEY):
                # Get all organizations of the user to search for the default
                if memberships is None:
                    memberships = OrganizationMember.objects.filter(
                        user=request.user
                    ).select_related("organization")

                # Search for the default organization
                default_membership = memberships.filter(is_default=True).first()
                if default_membership:
                    request.session[CURRENT_ORGANIZATION_SESSION_KEY] = (
                        default_membership.organization.id,
                        default_membership.organization.name,
                    )
                else:
                    # Use first organization from session
                    organizations = request.session[ORGANIZATIONS_SESSION_KEY]
                    if organizations:
                        request.session[CURRENT_ORGANIZATION_SESSION_KEY] = (
                            organizations[0]
                        )

        response = self.get_response(request)
        return response
