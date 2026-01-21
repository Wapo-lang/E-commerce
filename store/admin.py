from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Producto, Categoria, Devolucion  # 1. Asegúrate de importar Devolucion

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['mostrar_imagen', 'nombre', 'categoria', 'precio', 'stock', 'creado']
    list_filter = ['creado', 'categoria']
    list_editable = ['precio', 'stock']
    search_fields = ['nombre', 'descripcion']

    def mostrar_imagen(self, obj):
        if obj.imagen:
            return mark_safe(f'<img src="{obj.imagen}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />')
        return "Sin imagen"
    
    mostrar_imagen.short_description = 'Imagen'

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']

# --- NUEVO: REGISTRO DE DEVOLUCIONES ---
@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    # Mostramos datos útiles para identificar la devolución rápidamente
    list_display = ['id', 'get_usuario', 'get_producto', 'fecha', 'aprobada']
    list_filter = ['aprobada', 'fecha']
    search_fields = ['detalle__producto__nombre', 'detalle__orden__usuario__username', 'motivo']
    
    # Métodos para traer información desde las relaciones
    def get_usuario(self, obj):
        return obj.detalle.orden.usuario.username
    get_usuario.short_description = 'Cliente'

    def get_producto(self, obj):
        return obj.detalle.producto.nombre
    get_producto.short_description = 'Producto devuelto'

from .models import Orden

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'fecha', 'total', 'pagado']
    list_filter = ['fecha', 'pagado']