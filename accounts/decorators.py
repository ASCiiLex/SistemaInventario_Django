from django.http import HttpResponseForbidden


def permission_required_custom(permission_func):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):

            # 🔥 conectar user con request (clave multi-tenant)
            request.user._request = request

            if not permission_func(request.user):
                return HttpResponseForbidden()

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator