from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.db import transaction # Vital para transacciones seguras
from django.contrib.auth.models import Group, User
from .models import Categoria, Producto, Orden, DetalleOrden, Devolucion
from .carrito import Carrito
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def es_admin_inventario(user): 
    return user.is_authenticated and (user.groups.filter(name='Admin_Inventario').exists() or user.is_superuser)

def es_gestor_descuentos(user): 
    return user.is_authenticated and (user.groups.filter(name='Gestor_Descuentos').exists() or user.is_superuser)

def es_gestor_finanzas(user): 
    return user.is_authenticated and (user.groups.filter(name='Gestor_Finanzas').exists() or user.is_superuser)

@user_passes_test(lambda u: u.is_superuser)
def crear_empleado(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        rol_nombre = request.POST.get('rol') 
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, email=email, password=password)
                grupo = Group.objects.get(name=rol_nombre)
                user.groups.add(grupo)
                user.is_staff = True 
                user.save()
                messages.success(request, f"Empleado {username} creado exitosamente.")
            return redirect('crear_empleado')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    # --- ESTA ES LA PARTE QUE FALTA ---
    grupos = Group.objects.all()
    # Filtramos usuarios que son staff pero no superusuarios (opcional) para ver solo empleados
    empleados = User.objects.filter(is_staff=True).exclude(is_superuser=True)
    
    context = {
        'grupos': grupos,
        'users_staff': empleados # Este nombre debe coincidir con el del HTML
    }
    return render(request, 'store/admin_empleados.html', context)

@login_required
def checkout(request):
    carrito_obj = Carrito(request)
    if not carrito_obj.carrito:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('lista_productos')

    # Solo procesamos si viene por POST (al presionar el botón)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Calculamos el total
                total = sum(float(item['total']) for item in carrito_obj.carrito.values())
                
                # 1. Crear Orden inmediatamente
                orden = Orden.objects.create(
                    usuario=request.user,
                    total=total,
                    pagado=True
                )
                
                # 2. Procesar productos y stock
                for key, item in carrito_obj.carrito.items():
                    producto = Producto.objects.select_for_update().get(id=item['producto_id'])
                    cantidad = int(item['cantidad'])
                    
                    if producto.stock < cantidad:
                        raise Exception(f"Lo sentimos, ya no queda stock suficiente de {producto.nombre}")
                    
                    # Descontar stock
                    producto.stock -= cantidad
                    producto.save()
                    
                    # Crear detalle
                    DetalleOrden.objects.create(
                        orden=orden,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=item['precio']
                    )
                
                # 3. Limpiar carrito
                carrito_obj.limpiar() 
                
                messages.success(request, f"¡Compra finalizada con éxito! Orden #{orden.id}")
                return redirect('historial_compras')
                
        except Exception as e:
            messages.error(request, f"Error en la compra: {str(e)}")
            return redirect('ver_carrito')

    return redirect('ver_carrito')

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

@login_required
def gestionar_stock(request):
    # Verificación manual para enviar mensaje de error
    if not es_admin_inventario(request.user):
        messages.warning(request, "Acceso denegado: No tienes permisos para gestionar inventario.")
        return redirect('lista_productos')
        
    productos = Producto.objects.all()
    if request.method == 'POST':
        prod_id = request.POST.get('producto_id')
        nuevo_stock = int(request.POST.get('stock'))
        p = Producto.objects.get(id=prod_id)
        p.stock = nuevo_stock
        p.save()
        messages.success(request, "Stock actualizado")
    return render(request, 'store/gestion_stock.html', {'productos': productos})

@login_required
def ver_reportes(request):
    if not es_gestor_finanzas(request.user):
        messages.warning(request, "Acceso denegado: No tienes permisos para ver reportes financieros.")
        return redirect('lista_productos')

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
    busqueda = request.GET.get('buscar')
    
    if busqueda:
        # 1. Caso Búsqueda: Filtramos productos por nombre
        productos = Producto.objects.filter(nombre__icontains=busqueda)
        return render(request, 'store/lista.html', {
            'productos': productos, 
            'es_busqueda': True,
            'query': busqueda
        })
    
    # 2. Caso Catálogo: Agrupamos por categorías para la página principal
    # Usamos prefetch_related para que la carga sea ultra rápida
    categorias = Categoria.objects.all().prefetch_related('productos')
    
    return render(request, 'store/lista.html', {
        'categorias': categorias, 
        'es_busqueda': False
    })

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
    producto = get_object_or_404(Producto, id=id)
    
    # Intentamos agregar y verificamos el retorno del método de tu carrito.py
    if carrito.agregar(producto=producto):
        messages.success(request, f"¡{producto.nombre} añadido al carrito!")
    else:
        messages.error(request, f"No hay suficiente stock disponible de {producto.nombre}.")
    
    return redirect(request.META.get('HTTP_REFERER', 'ver_carrito'))

def restar_producto(request, id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=id)
    carrito.restar(producto=producto)
    return redirect("ver_carrito")

def eliminar_producto(request, id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=id)
    carrito.eliminar(producto=producto)
    messages.info(request, f"Se eliminó {producto.nombre} del carrito.")
    return redirect("ver_carrito")

def limpiar_carrito(request):
    request.session["carrito"] = {}
    request.session.modified = True
    return redirect("ver_carrito")

@login_required
def gestionar_descuentos(request):
    if not es_gestor_descuentos(request.user):
        messages.warning(request, "Acceso denegado: No tienes permisos para gestionar descuentos.")
        return redirect('lista_productos')

    productos = Producto.objects.all()
    if request.method == 'POST':
        prod_id = request.POST.get('producto_id')
        nuevo_desc = int(request.POST.get('descuento'))
        p = Producto.objects.get(id=prod_id)
        p.descuento_porcentaje = nuevo_desc
        p.save()
        messages.success(request, f"Descuento de {nuevo_desc}% aplicado a {p.nombre}")
        return redirect('gestionar_descuentos')
        
    return render(request, 'store/gestion_descuentos.html', {'productos': productos})

@login_required
def gestionar_devoluciones(request):
    # Permitir si es Superusuario O si es Gestor de Finanzas
    if not (request.user.is_superuser or es_gestor_finanzas(request.user)):
        messages.error(request, "Acceso restringido: Solo Finanzas o Administradores.")
        return redirect('lista_productos')

    if request.method == 'POST':
        dev_id = request.POST.get('dev_id')
        solicitud = get_object_or_404(Devolucion, id=dev_id)
        
        # Cambiamos el estado y aprobamos
        solicitud.aprobada = True
        # Si tienes un campo 'estado' en el modelo, actualízalo también
        if hasattr(solicitud, 'estado'):
            solicitud.estado = 'Aprobada'
            
        solicitud.save()
        
        # IMPORTANTE: Devolver el stock al producto tras aprobar
        detalle = solicitud.detalle
        producto = detalle.producto
        producto.stock += detalle.cantidad
        producto.save()
        
        messages.success(request, f"Devolución de {producto.nombre} aprobada. Stock actualizado.")
        return redirect('gestionar_devoluciones')

    devoluciones = Devolucion.objects.all().order_by('aprobada', '-fecha')
    return render(request, 'store/gestion_devoluciones.html', {'devoluciones': devoluciones})

def ver_categoria(request, categoria_id):
    # 1. Buscamos la categoría específica
    categoria_seleccionada = get_object_or_404(Categoria, id=categoria_id)
    
    # 2. Filtramos los productos que pertenecen a esa categoría
    productos = Producto.objects.filter(categoria=categoria_seleccionada)

    return render(request, 'store/lista.html', {
        'productos': productos,
        'es_busqueda': True, 
        'query': categoria_seleccionada.nombre # Esto hará que el título diga: Resultados para: "Smartphones"
    })

@login_required
def rechazar_devolucion(request, devolucion_id):
    # Verificación de autoridad
    if not (request.user.is_superuser or es_gestor_finanzas(request.user)):
        messages.error(request, "No tienes permiso para rechazar devoluciones.")
        return redirect('lista_productos')

    if request.method == 'POST':
        devolucion = get_object_or_404(Devolucion, id=devolucion_id)
        motivo = request.POST.get('motivo_rechazo')
        
        if not motivo:
            messages.error(request, "Debes ingresar un motivo para rechazar.")
            return redirect('gestionar_devoluciones')

        devolucion.aprobada = False
        # Asegúrate de que tu modelo tenga 'estado' y 'motivo_rechazo'
        devolucion.motivo_rechazo = motivo
        if hasattr(devolucion, 'estado'):
            devolucion.estado = 'Rechazada'
        
        devolucion.save()
        messages.warning(request, f"Solicitud #{devolucion.id} rechazada.")
        
    return redirect('gestionar_devoluciones')