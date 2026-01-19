import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from store.models import Producto, Orden, Devolucion

def crear_grupos():
    roles = {
        'Admin_Inventario': [Producto], # Puede editar stocks
        'Gestor_Descuentos': [Producto], # Puede editar precios/descuentos
        'Gestor_Finanzas': [Orden, Devolucion], # Ve reportes y devoluciones
    }

    for nombre_rol, modelos in roles.items():
        grupo, created = Group.objects.get_or_create(name=nombre_rol)
        print(f"Grupo '{nombre_rol}' configurado.")
        # Aquí podrías asignar permisos específicos si quisieras hilar muy fino
        # Por ahora, verificaremos la pertenencia al grupo en las views.

if __name__ == '__main__':
    crear_grupos()