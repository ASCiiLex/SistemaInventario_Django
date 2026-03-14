from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone

from ..models import Order
from ..forms import (
    OrderForm,
    OrderItemFormSet,
    OrderFilterForm,
    OrderReceiveForm,
)


def order_list(request):
    qs = Order.objects.select_related("supplier", "location").all()

    filter_form = OrderFilterForm(request.GET or None)
    if filter_form.is_valid():
        supplier = filter_form.cleaned_data.get("supplier")
        location = filter_form.cleaned_data.get("location")
        status = filter_form.cleaned_data.get("status")

        if supplier:
            qs = qs.filter(supplier=supplier)
        if location:
            qs = qs.filter(location=location)
        if status:
            qs = qs.filter(status=status)

    paginator = Paginator(qs, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "orders": page_obj,
        "page_obj": page_obj,
        "filter_form": filter_form,
    }

    if request.headers.get("HX-Request"):
        return render(request, "inventory/orders/partials/table.html", context)

    return render(request, "inventory/orders/list.html", context)


def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save()
            formset.instance = order
            formset.save()
            messages.success(request, "Pedido creado correctamente.")
            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(
        request,
        "inventory/orders/form.html",
        {"form": form, "formset": formset, "title": "Nuevo pedido"},
    )


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "inventory/orders/detail.html", {"order": order})


def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if order.status not in ["pending", "backordered"]:
        messages.error(request, "Este pedido no se puede editar en su estado actual.")
        return redirect("order_detail", pk=pk)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Pedido actualizado correctamente.")
            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)

    return render(
        request,
        "inventory/orders/form.html",
        {"form": form, "formset": formset, "title": f"Editar pedido #{order.id}"},
    )


def order_send(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if order.status != "pending":
        messages.error(request, "Solo se pueden marcar como enviados los pedidos pendientes.")
        return redirect("order_detail", pk=pk)

    order.status = "sent"
    order.sent_at = timezone.now()
    order.save()
    messages.success(request, "Pedido marcado como enviado.")
    return redirect("order_detail", pk=pk)


def order_receive(request, pk):
    order = get_object_or_404(Order, pk=pk)

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


def order_cancel(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if order.status in ["received", "cancelled"]:
        messages.error(request, "Este pedido no se puede cancelar.")
        return redirect("order_detail", pk=pk)

    order.status = "cancelled"
    order.save()
    messages.success(request, "Pedido cancelado correctamente.")
    return redirect("order_detail", pk=pk)