from django.shortcuts import render, redirect, get_object_or_404
from .models import Movement
from .forms import MovementForm

def movement_list(request):
    movements = Movement.objects.all()
    return render(request, 'movements/list.html', {'movements': movements})

def movement_create(request):
    if request.method == 'POST':
        form = MovementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('movement_list')
    else:
        form = MovementForm()
    return render(request, 'movements/form.html', {'form': form})