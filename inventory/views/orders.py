from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string

from ..models import Order
from ..forms import (
    OrderForm,
    OrderItemFormSet,
    OrderFilterForm,
    OrderReceiveForm,
)
from ..utils.listing import ListViewMixin

from accounts.permissions import (
    can_create_inventory,
    can_edit_inventory,
    can_confirm_inventory,
)
from accounts.decorators import permission_required_custom


def order_list(request):
    view = ListViewMixin()
    view.allowed_sort_fields = [
        "id",
        "supplier__name",
        "location__name",
        "status",
        "created_at",
    ]
    view.default_ordering = "-created_at"

    qs = Order.objects.select_related("supplier", "location").filter(
        organization=request.organization
    )

    filter_form = OrderFilterForm(
        request.GET or None,
        organization=request.organization
    )

    if filter_form.is_valid():
        data = filter_form.cleaned_data

        if data.get("supplier"):
            qs = qs.filter(supplier=data["supplier"])
        if data.get("location"):
            qs = qs.filter(location=data["location"])
        if data.get("status"):
            qs = qs.filter(status=data["status"])

    qs = view.apply_ordering(request, qs)
    page_obj = view.paginate_queryset(request, qs)

    context = {
        "orders": page_obj,
        "page_obj": page_obj,
        "filter_form": filter_form,
        **view.get_ordering_context(request),
    }

    if view.is_htmx(request):
        return render(request, "inventory/orders/partials/table.html", context)

    return render(request, "inventory/orders/list.html", context)


@permission_required_custom(can_create_inventory)
def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST, organization=request.organization)
        formset = OrderItemFormSet(
            request.POST,
            form_kwargs={"organization": request.organization}
        )

        if form.is_valid() and formset.is_valid():
            order = form.save()

            formset.instance = order
            formset.save()

            messages.success(request, "Pedido creado correctamente.")
            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderForm(organization=request.organization)
        formset = OrderItemFormSet(
            form_kwargs={"organization": request.organization}
        )

    return render(
        request,
        "inventory/orders/form.html",
        {
            "form": form,
            "formset": formset,
            "title": "Nuevo pedido",
        },
    )


def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related("supplier", "location")
        .prefetch_related("items__product"),
        pk=pk,
        organization=request.organization
    )

    return render(
        request,
        "inventory/orders/detail.html",
        {
            "order": order,
            "can_edit": can_edit_inventory(request.user),
            "can_confirm": can_confirm_inventory(request.user),
            "can_receive": order.status in ("sent", "partially_received", "backordered"),
            "can_cancel": order.status not in ("received", "cancelled"),
        },
    )


@permission_required_custom(can_edit_inventory)
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk, organization=request.organization)

    if order.status not in ["pending", "backordered"]:
        messages.error(request, "Este pedido no se puede editar en su estado actual.")
        return redirect("order_detail", pk=pk)

    if request.method == "POST":
        form = OrderForm(
            request.POST,
            instance=order,
            organization=request.organization
        )
        formset = OrderItemFormSet(
            request.POST,
            instance=order,
            form_kwargs={"organization": request.organization}
        )

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()

            messages.success(request, "Pedido actualizado correctamente.")
            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderForm(
            instance=order,
            organization=request.organization
        )
        formset = OrderItemFormSet(
            instance=order,
            form_kwargs={"organization": request.organization}
        )

    return render(
        request,
        "inventory/orders/form.html",
        {
            "form": form,
            "formset": formset,
            "title": f"Editar pedido #{order.id}",
        },
    )


@permission_required_custom(can_confirm_inventory)
def order_send(request, pk):
    order = get_object_or_404(Order, pk=pk, organization=request.organization)

    if order.status != "pending":
        messages.error(request, "Solo se pueden marcar como enviados los pedidos pendientes.")
        return redirect("order_detail", pk=pk)

    order.status = "sent"
    order.sent_at = timezone.now()
    order.save()

    messages.success(request, "Pedido marcado como enviado.")
    return redirect("order_detail", pk=pk)


@permission_required_custom(can_confirm_inventory)
def order_receive(request, pk):
    order = get_object_or_404(Order, pk=pk, organization=request.organization)

    if order.status not in ["sent", "partially_received", "backordered"]:
        messages.error(request, "Este pedido no se puede marcar como recibido.")
        return redirect("order_detail", pk=pk)

    if request.method == "POST":
        form = OrderReceiveForm(request.POST)
        if form.is_valid():
            order.status = "received"
            order.received_at = timezone.now()
            order.save()

            messages.success(request, "Pedido marcado como recibido.")
            return redirect("order_detail", pk=pk)
    else:
        form = OrderReceiveForm()

    return render(
        request,
        "inventory/orders/receive.html",
        {"order": order, "form": form},
    )


@permission_required_custom(can_confirm_inventory)
def order_cancel(request, pk):
    order = get_object_or_404(Order, pk=pk, organization=request.organization)

    if order.status in ["received", "cancelled"]:
        messages.error(request, "Este pedido no se puede cancelar.")
        return redirect("order_detail", pk=pk)

    order.status = "cancelled"
    order.save()

    messages.success(request, "Pedido cancelado correctamente.")
    return redirect("order_detail", pk=pk)


def orders_counter(request):
    pending = Order.objects.filter(
        organization=request.organization,
        status__in=["pending", "partially_received", "backordered"]
    ).count()

    html = render_to_string(
        "inventory/orders/partials/counter.html",
        {"pending": pending}
    )

    response = HttpResponse(html)
    response["HX-Trigger"] = '{"orders:updated": true}'
    return response