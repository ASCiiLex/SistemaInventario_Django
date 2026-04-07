from django.http import HttpResponseForbidden


def permission_required_custom(permission_func):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):

            request.user._request = request

            print("------ DEBUG PERMISSIONS ------")
            print("USER:", request.user)
            print("ORG:", getattr(request, "organization", None))

            result = permission_func(request.user)

            print("PERMISSION RESULT:", result)
            print("-------------------------------")

            if not result:
                return HttpResponseForbidden("No tienes permisos para acceder a auditoría.")

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator