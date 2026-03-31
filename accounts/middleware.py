from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Fuerza autenticación global en toda la app.
    Compatible con HTMX (no rompe peticiones parciales).
    """

    EXEMPT_URLS = [
        "login",
        "logout",
        "admin:login",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            current_path = request.path

            exempt_paths = [reverse(url) for url in self.EXEMPT_URLS]

            if not any(current_path.startswith(path) for path in exempt_paths):
                # 🔥 HTMX → no redirigir normal (rompe UI)
                if request.headers.get("HX-Request"):
                    response = redirect("login")
                    response["HX-Redirect"] = reverse("login")
                    return response

                return redirect("login")

        return self.get_response(request)