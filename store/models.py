from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# --- Tus modelos existentes (ligeramente mejorados) ---
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self): return self.nombre

class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, related_name='productos', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.CharField(max_length=500, null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    # Nuevo campo para descuento directo
    descuento_porcentaje = models.IntegerField(default=0, help_text="0 a 100")

    def __str__(self): return self.nombre

    @property
    def precio_final(self):
        # Calcula el precio con descuento
        if self.descuento_porcentaje > 0:
            return self.precio * (1 - self.descuento_porcentaje / 100)
        return self.precio

# --- NUEVOS MODELOS PARA EL E-COMMERCE ---

class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ordenes')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)
    
    def __str__(self): return f"Orden #{self.id} - {self.usuario.username}"

class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) # Si borran el producto, queda el registro
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Precio al momento de comprar
    
    # Control de devoluciones
    devuelto = models.BooleanField(default=False)

class Devolucion(models.Model):
    detalle = models.OneToOneField(DetalleOrden, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField()
    aprobada = models.BooleanField(default=False)