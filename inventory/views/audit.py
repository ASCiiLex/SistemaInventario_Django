from django.shortcuts import render

from accounts.permissions import can_view_audit
from accounts.decorators import permission_required_custom

from ..models.audit import AuditLog
from ..utils.listing import ListViewMixin
from ..forms.audit import AuditFilterForm
from inventory.services.audit import format_changes


@permission_required_custom(can_view_audit)
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

    qs = (
        AuditLog.objects
        .select_related("user")
        .filter(organization=request.organization)
    )

    filter_form = AuditFilterForm(request.GET or None)

    if filter_form.is_valid():
        data = filter_form.cleaned_data

        if data.get("action"):
            qs = qs.filter(action=data["action"])

        if data.get("model"):
            qs = qs.filter(model_name__icontains=data["model"])

        if data.get("user"):
            qs = qs.filter(user__username__icontains=data["user"])

        if data.get("date_from"):
            qs = qs.filter(created_at__date__gte=data["date_from"])

        if data.get("date_to"):
            qs = qs.filter(created_at__date__lte=data["date_to"])

    qs = view.apply_ordering(request, qs)
    page_obj = view.paginate_queryset(request, qs)

    logs = []
    for log in page_obj:
        log.formatted_changes = format_changes(log.changes)
        log.has_changes = bool(log.formatted_changes)
        logs.append(log)

    context = {
        "logs": logs,
        "page_obj": page_obj,
        "filter_form": filter_form,
        "total_count": qs.count(),
        **view.get_ordering_context(request),
    }

    if view.is_htmx(request):
        return render(request, "inventory/audit/partials/table.html", context)

    return render(request, "inventory/audit/list.html", context)