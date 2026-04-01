def organization(request):
    return {
        "organization": getattr(request, "organization", None)
    }