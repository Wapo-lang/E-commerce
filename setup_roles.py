import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from store.models import Producto, Orden, Devolucion

def crear_grupos():
    roles_permisos = {
        'Admin_Inventario': {
            'modelos': [Producto],
            'acciones': ['add', 'change', 'view']
        },
        'Gestor_Descuentos': {
            'modelos': [Producto],
            'acciones': ['change', 'view']
        },
        'Gestor_Finanzas': {
            'modelos': [Orden, Devolucion],
            'acciones': ['view', 'change']
        },
    }

    for nombre_rol, config in roles_permisos.items():
        grupo, created = Group.objects.get_or_create(name=nombre_rol)
        
        for modelo in config['modelos']:
            # Obtenemos el ID del tipo de contenido para el modelo
            ct = ContentType.objects.get_for_model(modelo)
            
            # Buscamos los permisos (ej: 'change_producto')
            for accion in config['acciones']:
                codenome = f"{accion}_{modelo._meta.model_name}"
                try:
                    permiso = Permission.objects.get(content_type=ct, codename=codenome)
                    grupo.permissions.add(permiso)
                except Permission.DoesNotExist:
                    print(f"Error: Permiso {codenome} no encontrado.")

        print(f"✅ Grupo '{nombre_rol}' configurado con permisos.")

if __name__ == '__main__':
    crear_grupos()