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

from inventory.services.audit import log_action, serialize_instance, get_instance_changes


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

    filter_form = OrderFilterForm(request.GET or None)

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

    return render(request, "inventory/orders/list.html", {
        "orders": page_obj,
        "page_obj": page_obj,
        "filter_form": filter_form,
        **view.get_ordering_context(request),
    })


@permission_required_custom(can_create_inventory)
def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.organization = request.organization
            order.save()

            formset.instance = order
            formset.save()

            log_action(request.user, "CREATE", order, serialize_instance(order))

            messages.success(request, "Pedido creado correctamente.")
            return redirect("order_detail", pk=order.pk)

    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, "inventory/orders/form.html", {
        "form": form,
        "formset": formset,
        "title": "Nuevo pedido",
    })


def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related("supplier", "location")
        .prefetch_related("items__product"),
        pk=pk,
        organization=request.organization
    )

    return render(request, "inventory/orders/detail.html", {
        "order": order,
        "can_edit": can_edit_inventory(request.user),
        "can_confirm": can_confirm_inventory(request.user),
        "can_receive": order.status in ("sent", "partially_received", "backordered"),
        "can_cancel": order.status not in ("received", "cancelled"),
    })


@permission_required_custom(can_edit_inventory)
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk, organization=request.organization)
    old_data = serialize_instance(order)

    if order.status not in ["pending", "backordered"]:
        return redirect("order_detail", pk=pk)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()

            changes = get_instance_changes(old_data, order)
            if changes:
                log_action(request.user, "UPDATE", order, changes)

            return redirect("order_detail", pk=order.pk)

    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)

    return render(request, "inventory/orders/form.html", {
        "form": form,
        "formset": formset,
        "title": f"Editar pedido #{order.id}",
    })


@permission_required_custom(can_confirm_inventory)
def order_send(request, pk):
    order = get_object_or_404(Order, pk=pk, organization=request.organization)

    if order.status != "pending":
        return redirect("order_detail", pk=pk)

    order.status = "sent"
    order.sent_at = timezone.now()
    order.save()

    return redirect("order_detail", pk=pk)


@permission_required_custom(can_confirm_inventory)
def order_receive(request, pk):
    order = get_object_or_404(Order, pk=pk, organization=request.organization)

    if request.method == "POST":
        form = OrderReceiveForm(request.POST)
        if form.is_valid():
            order.status = "received"
            order.received_at = timezone.now()
            order.save()

            return redirect("order_detail", pk=pk)
    else:
        form = OrderReceiveForm()

    return render(request, "inventory/orders/receive.html", {
        "order": order,
        "form": form,
    })


@permission_required_custom(can_confirm_inventory)
def order_cancel(request, pk):
    order = get_object_or_404(Order, pk=pk, organization=request.organization)

    order.status = "cancelled"
    order.save()

    return redirect("order_detail", pk=pk)


def orders_counter(request):
    pending = Order.objects.filter(
        organization=request.organization,
        status="pending"
    ).count()

    html = render_to_string(
        "inventory/orders/partials/counter.html",
        {"pending": pending}
    )

    return HttpResponse(html)