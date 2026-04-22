from django.http import HttpResponse
from django.contrib.auth.models import User


def create_admin(request):
    if User.objects.filter(username="admin").exists():
        return HttpResponse("ya existe")

    user = User.objects.create_superuser(
        username="admin",
        email="admin@demo.com",
        password="admin1234"
    )

    return HttpResponse("admin creado")