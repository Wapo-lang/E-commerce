from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.db import transaction # Vital para transacciones seguras
from django.contrib.auth.models import Group, User
from .models import Producto, Orden, DetalleOrden, Devolucion
from .carrito import Carrito
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def es_admin_inventario(user): 
    return user.groups.filter(name='Admin_Inventario').exists() or user.is_superuser

def es_gestor_descuentos(user): 
    return user.groups.filter(name='Gestor_Descuentos').exists() or user.is_superuser

def es_gestor_finanzas(user): 
    return user.groups.filter(name='Gestor_Finanzas').exists() or user.is_superuser


@user_passes_test(lambda u: u.is_superuser)
def crear_empleado(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        rol = request.POST['rol'] # 'Admin_Inventario', etc.
        
        try:
            user = User.objects.create_user(username, email, password)
            grupo = Group.objects.get(name=rol)
            user.groups.add(grupo)
            user.is_staff = True # Necesario para entrar a ciertas áreas si usas admin
            user.save()
            messages.success(request, f"Empleado {username} creado como {rol}")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    grupos = Group.objects.all()
    return render(request, 'store/admin_empleados.html', {'grupos': grupos})

@login_required
def checkout(request):
    carrito = Carrito(request)
    if not carrito.carrito:
        return redirect('lista_productos')

    # Calcular total
    total = sum(float(item['total']) for item in carrito.carrito.values())

    if request.method == 'POST':
        # Simulación de pago (aquí validarías la tarjeta)
        # numero_tarjeta = request.POST.get('tarjeta') ...
        
        try:
            with transaction.atomic(): # Si algo falla, se revierte todo
                # 1. Crear Orden
                orden = Orden.objects.create(
                    usuario=request.user,
                    total=total,
                    pagado=True
                )
                
                # 2. Mover items del carrito a la DB y Restar Stock
                for key, item in carrito.carrito.items():
                    producto = Producto.objects.select_for_update().get(id=item['producto_id'])
                    cantidad = item['cantidad']
                    
                    if producto.stock < cantidad:
                        raise Exception(f"No hay suficiente stock de {producto.nombre}")
                    
                    # Restar stock
                    producto.stock -= cantidad
                    producto.save()
                    
                    # Crear detalle
                    DetalleOrden.objects.create(
                        orden=orden,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=item['precio']
                    )
                
                # 3. Limpiar carrito y Redirigir
                carrito.limpiar()
                messages.success(request, "¡Compra exitosa!")
                return redirect('historial_compras')
                
        except Exception as e:
            messages.error(request, f"Error en la compra: {str(e)}")
            return redirect('ver_carrito')

    return render(request, 'store/checkout.html', {'total': total})

@login_required
def historial_compras(request):
    ordenes = Orden.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'store/historial.html', {'ordenes': ordenes})

@login_required
def solicitar_devolucion(request, detalle_id):
    detalle = get_object_or_404(DetalleOrden, id=detalle_id, orden__usuario=request.user)
    
    if request.method == 'POST':
        if not detalle.devuelto:
            motivo = request.POST.get('motivo')
            Devolucion.objects.create(detalle=detalle, motivo=motivo)
            messages.info(request, "Solicitud de devolución enviada.")
        return redirect('historial_compras')
    
    return render(request, 'store/devolucion_form.html', {'detalle': detalle})

@user_passes_test(es_admin_inventario)
def gestionar_stock(request):
    productos = Producto.objects.all()
    if request.method == 'POST':
        prod_id = request.POST.get('producto_id')
        nuevo_stock = int(request.POST.get('stock'))
        p = Producto.objects.get(id=prod_id)
        p.stock = nuevo_stock
        p.save()
        messages.success(request, "Stock actualizado")
    return render(request, 'store/gestion_stock.html', {'productos': productos})

@user_passes_test(es_gestor_finanzas)
def ver_reportes(request):
    ordenes = Orden.objects.all().order_by('-fecha')
    devoluciones = Devolucion.objects.all()
    total_vendido = sum(o.total for o in ordenes)
    return render(request, 'store/reportes.html', {
        'ordenes': ordenes, 
        'devoluciones': devoluciones,
        'total_vendido': total_vendido
    })

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