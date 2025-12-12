"""
Context processors for templates.
"""

from core.middleware import ORGANIZATION_ID_SESSION_KEY, ORGANIZATIONS_SESSION_KEY


def organization_context(request):
    """Add organization information to the template context."""
    return {
        "user_organizations": request.session.get(ORGANIZATIONS_SESSION_KEY, []),
        "current_organization": request.session.get(ORGANIZATION_ID_SESSION_KEY, None),
    }
