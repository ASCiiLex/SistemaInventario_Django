from django.shortcuts import render, redirect, get_object_or_404
from .models import Supplier
from .forms import SupplierForm

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'suppliers/list.html', {'suppliers': suppliers})

def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'suppliers/form.html', {'form': form})

def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'suppliers/form.html', {'form': form})

def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return redirect('supplier_list')