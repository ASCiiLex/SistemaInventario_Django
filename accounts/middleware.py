from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch


class LoginRequiredMiddleware:
    """
    🔐 Fuerza login en toda la app excepto rutas públicas
    """


    EXEMPT_PREFIXES = [
        "/static/",
        "/media/",
        "/metrics/",
        "/login",
        "/logout",
        "/create-admin",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # permitir siempre recursos estáticos / internos
        path = request.path

        if any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
            return self.get_response(request)

        # evitar problemas si request.user no está listo aún
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            return self.get_response(request)

        exempt_paths = []
        for url in self.EXEMPT_URLS:
            try:
                exempt_paths.append(reverse(url))
            except NoReverseMatch:
                continue

        if any(path.startswith(url) for url in exempt_paths):
            return self.get_response(request)

        return redirect("login")