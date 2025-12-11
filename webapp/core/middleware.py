"""
Custom Middleware
"""


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
