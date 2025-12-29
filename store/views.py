from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto
from .carrito import Carrito

def lista_productos(request):
    # Traemos todos los productos disponibles de la base de datos
    productos = Producto.objects.filter(disponible=True)
    return render(request, 'store/lista.html', {'productos': productos})

def detalle_producto(request, id):
    # Busca el producto por su ID o lanza un error 404 si no existe
    producto = get_object_or_404(Producto, id=id, disponible=True)
    return render(request, 'store/detalle.html', {'producto': producto})

def agregar_producto(request, id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=id)
    carrito.agregar(producto=producto)
    return redirect("lista_productos")