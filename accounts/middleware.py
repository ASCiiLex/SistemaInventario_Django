from django.shortcuts import redirect
from django.urls import resolve


class LoginRequiredMiddleware:
    """
    🔐 Fuerza login en toda la app excepto rutas públicas
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

        # 2) Resolver nombre de la URL (robusto con fallback)
        url_name = None
        try:
            match = resolve(path)
            url_name = match.url_name
        except Exception:
            pass

        # 🔥 fallback directo por path (evita problemas de resolución)
        if url_name in self.EXEMPT_NAMES or path.startswith("/create-admin"):
            return self.get_response(request)

        # 3) Usuario autenticado
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            return self.get_response(request)

        return redirect("login")