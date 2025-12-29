from django.urls import path
from .views import *
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', lista_productos, name='lista_productos'),
    path('producto/<int:id>/', detalle_producto, name='detalle_producto'),
    path('agregar/<int:id>/', agregar_producto, name='agregar'), # Nueva ruta
]