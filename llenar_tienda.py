import os
import django

# 1. Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') 
django.setup()

from store.models import Producto, Categoria

def poblar():
    catalogo = {
        "Smartphones": [
            {
                "nombre": "iPhone 15 Pro",
                "precio": 999,
                "img": "https://images.unsplash.com/photo-1695048132832-b41495f12eb4?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
            },
            {
                "nombre": "Samsung Galaxy S24",
                "precio": 899,
                "img": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?q=80&w=500&auto=format&fit=crop"
            }
        ],
        "Laptops": [
            {
                "nombre": "MacBook Air M3",
                "precio": 1200,
                "img": "https://images.unsplash.com/photo-1517336714460-4c50d917805d?q=80&w=500&auto=format&fit=crop"
            },
            {
                "nombre": "Dell XPS 13",
                "precio": 1100,
                "img": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?q=80&w=500&auto=format&fit=crop"
            }
        ],
        "Audio": [
            {
                "nombre": "Sony WH-1000XM5",
                "precio": 350,
                "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=500&auto=format&fit=crop"
            }
        ]
    }

    print("--- Limpiando base de datos ---")
    Producto.objects.all().delete()
    Categoria.objects.all().delete()

    for nombre_cat, productos in catalogo.items():
        cat_obj, _ = Categoria.objects.get_or_create(nombre=nombre_cat)
        
        for p in productos:
            Producto.objects.create(
                categoria=cat_obj,
                nombre=p["nombre"],
                descripcion=f"Edición especial de {p['nombre']} disponible en I-BEY.",
                precio=p["precio"],
                stock=15,
                imagen=p["img"]
            )
            print(f"Cargado: {p['nombre']}")

    print("DATOS CARGADOS EXITOSAMENTE")

if __name__ == '__main__':
    poblar()