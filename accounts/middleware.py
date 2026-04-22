from django.shortcuts import redirect
from django.urls import resolve


class LoginRequiredMiddleware:
    """
    🔐 Fuerza login en toda la app excepto rutas públicas
    (basado en url_name → determinista)
    """

    EXEMPT_NAMES = {
        "login",
        "logout",
        "create-admin",
    }

    EXEMPT_PREFIXES = (
        "/static/",
        "/media/",
        "/metrics/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # 1) Recursos estáticos/infra
        if path.startswith(self.EXEMPT_PREFIXES):
            return self.get_response(request)

        # 2) Resolver nombre de la URL
        try:
            match = resolve(path)
            url_name = match.url_name
        except Exception:
            url_name = None

        if url_name in self.EXEMPT_NAMES:
            return self.get_response(request)

        # 3) Usuario autenticado
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            return self.get_response(request)

        return redirect("login")