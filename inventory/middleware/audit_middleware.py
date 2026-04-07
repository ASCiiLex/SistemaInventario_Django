from .audit_user import set_current_user


class AuditUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_user(getattr(request, "user", None))
        return self.get_response(request)