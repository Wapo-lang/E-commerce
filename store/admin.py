from django.contrib import admin
from .models import Categoria, Producto
from django.utils.safestring import mark_safe # Para mostrar la imagen en el admin

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Columnas que verás en la lista de productos
    list_display = ['mostrar_imagen', 'nombre', 'categoria', 'precio', 'stock', 'disponible', 'creado']
    # Filtros laterales
    list_filter = ['disponible', 'creado', 'categoria']
    # Campos que se pueden editar sin entrar al detalle
    list_editable = ['precio', 'stock', 'disponible']
    # Buscador
    search_fields = ['nombre', 'descripcion']

    # Función para mostrar una miniatura de la imagen en la lista
    def mostrar_imagen(self, obj):
        if obj.imagen:
            return mark_safe(f'<img src="{obj.imagen.url}" width="50" height="50" style="object-fit: cover;" />')
        return "Sin imagen"
    
    mostrar_imagen.short_description = 'Imagen'