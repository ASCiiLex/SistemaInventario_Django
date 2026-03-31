from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ..models.audit import AuditLog
from ..utils.listing import ListViewMixin


@login_required
def audit_list(request):
    view = ListViewMixin()
    view.allowed_sort_fields = [
        "created_at",
        "action",
        "model_name",
        "object_id",
        "user__username",
    ]
    view.default_ordering = "-created_at"

    qs = AuditLog.objects.select_related("user").all()

    # 🔍 filtros básicos
    action = request.GET.get("action")
    model = request.GET.get("model")
    user = request.GET.get("user")

    if action:
        qs = qs.filter(action=action)

    if model:
        qs = qs.filter(model_name__icontains=model)

    if user:
        qs = qs.filter(user__username__icontains=user)

    qs = view.apply_ordering(request, qs)
    page_obj = view.paginate_queryset(request, qs)

    context = {
        "logs": page_obj,
        "page_obj": page_obj,
        **view.get_ordering_context(request),
    }

    if view.is_htmx(request):
        return render(request, "inventory/audit/partials/table.html", context)

    return render(request, "inventory/audit/list.html", context)