from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

urlpatterns = [
    # --- Tienda Pública ---
    path('', views.lista_productos, name='lista_productos'),
    path('categoria/<int:categoria_id>/', views.ver_categoria, name='ver_categoria'),
    path('producto/<int:id>/', views.detalle_producto, name='detalle_producto'),
    
    # --- Carrito (Lógica) ---
    path('agregar/<int:id>/', views.agregar_producto, name='agregar'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar/<int:id>/', views.eliminar_producto, name="eliminar"),
    path('restar/<int:id>/', views.restar_producto, name="restar"),
    path('limpiar/', views.limpiar_carrito, name='limpiar_carrito'),

    # --- Checkout y Compras (NUEVO) ---
    path('checkout/', views.checkout, name='checkout'),
    path('mis-compras/', views.historial_compras, name='historial_compras'),
    path('devolucion/<int:detalle_id>/', views.solicitar_devolucion, name='solicitar_devolucion'),
    path('staff/devoluciones/', views.gestionar_devoluciones, name='gestionar_devoluciones'),

    # --- Gestión Interna (Staff/Admin) (NUEVO) ---
    path('staff/crear-empleado/', views.crear_empleado, name='crear_empleado'),
    path('staff/stock/', views.gestionar_stock, name='gestionar_stock'),
    path('staff/reportes/', views.ver_reportes, name='ver_reportes'),
    path('staff/descuentos/', views.gestionar_descuentos, name='gestionar_descuentos'),
    # Devoluciones
    path('devolucion/rechazar/<int:devolucion_id>/', views.rechazar_devolucion, name='rechazar_devolucion'),

    # --- Autenticación ---
    path('registro/', views.registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]