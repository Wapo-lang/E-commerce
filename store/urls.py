from django.urls import path
from .views import *
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', lista_productos, name='lista_productos'),
    path('producto/<int:id>/', detalle_producto, name='detalle_producto'),
    path('agregar/<int:id>/', agregar_producto, name='agregar'), # Nueva ruta

    #Gestion de Usuarios
    path('login/', auth_views.LoginView.as_view(), name = 'login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name = 'logout'),

    #Cambio de cantraseña
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('registro/', registro, name='registro'),
]