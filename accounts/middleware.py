from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    🔐 Fuerza login en toda la app excepto rutas públicas
    """

    EXEMPT_URLS = [
        "login",
        "logout",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            return self.get_response(request)

        path = request.path

        exempt_paths = [reverse(url) for url in self.EXEMPT_URLS]

        if any(path.startswith(url) for url in exempt_paths):
            return self.get_response(request)

        return redirect("login")