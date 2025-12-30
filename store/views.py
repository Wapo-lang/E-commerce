from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Producto
from .carrito import Carrito

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Loguear al usuario automáticamente tras registrarse
            login(request, user) 
            return redirect('lista_productos')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/registro.html', {'form': form})

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