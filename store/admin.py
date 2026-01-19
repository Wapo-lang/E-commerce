from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Producto, Categoria

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # 1. Quitamos 'disponible' de list_display
    list_display = ['mostrar_imagen', 'nombre', 'categoria', 'precio', 'stock', 'creado']
    
    # 2. Quitamos 'disponible' de list_filter
    list_filter = ['creado', 'categoria']
    
    # 3. Quitamos 'disponible' de list_editable
    list_editable = ['precio', 'stock']
    
    search_fields = ['nombre', 'descripcion']

    # Función corregida para mostrar miniaturas con la nueva URL de texto
    def mostrar_imagen(self, obj):
        if obj.imagen:
            # Quitamos .url porque ahora obj.imagen es directamente el link
            return mark_safe(f'<img src="{obj.imagen}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />')
        return "Sin imagen"
    
    mostrar_imagen.short_description = 'Imagen'

# No olvides registrar también la categoría si no lo has hecho
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']