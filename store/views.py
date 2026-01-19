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
            login(request, user) 
            return redirect('lista_productos')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

def lista_productos(request):
    productos = Producto.objects.all() # Traemos todos
    query = request.GET.get('buscar')
    if query:
        productos = productos.filter(nombre__icontains=query)   
    return render(request, 'store/lista.html', {'productos': productos})

def detalle_producto(request, id):
    # Buscamos solo por ID
    producto = get_object_or_404(Producto, id=id)
    return render(request, 'store/detalle.html', {'producto': producto})

def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    # Cambiamos a float para evitar errores con Decimal
    total = sum(float(item['precio']) * item['cantidad'] for item in carrito.values())
    
    return render(request, 'store/carrito.html', {
        'carrito': carrito,
        'total': total
    })

# ... El resto de tus funciones (agregar, eliminar, restar, limpiar) están bien ...
def agregar_producto(request, id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=id)
    carrito.agregar(producto=producto)
    return redirect("ver_carrito")

def eliminar_producto(request, id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=id)
    carrito.eliminar(producto=producto)
    return redirect("ver_carrito")

def restar_producto(request, id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=id)
    carrito.restar(producto=producto)
    return redirect("ver_carrito")

def limpiar_carrito(request):
    request.session["carrito"] = {}
    request.session.modified = True
    return redirect("ver_carrito")