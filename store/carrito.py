# store/carrito.py
class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carrito = self.session.get("carrito")
        if not carrito:
            carrito = self.session["carrito"] = {}
        self.carrito = carrito

    def agregar(self, producto):
        id = str(producto.id)
        
        # Validación de Stock Crítica
        cantidad_actual_en_carrito = 0
        if id in self.carrito:
            cantidad_actual_en_carrito = self.carrito[id]["cantidad"]
            
        if cantidad_actual_en_carrito + 1 > producto.stock:
            return False 

        if id not in self.carrito.keys():
            self.carrito[id] = {
                "producto_id": producto.id,
                "nombre": producto.nombre,
                # --- AQUÍ ESTÁ EL CAMBIO ---
                # Usamos precio_venta (que ya incluye el IVA del modelo)
                "precio": str(float(producto.precio_venta)), 
                "cantidad": 1,
                "total": str(float(producto.precio_venta)),
                # ---------------------------
                "imagen": producto.imagen if producto.imagen else "",
            }
        else:
            self.carrito[id]["cantidad"] += 1
            precio = float(self.carrito[id]["precio"])
            self.carrito[id]["total"] = str(precio * self.carrito[id]["cantidad"])
            
        self.guardar_carrito()
        return True 

    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def eliminar(self, producto):
        id = str(producto.id)
        if id in self.carrito:
            del self.carrito[id]
            self.guardar_carrito()

    def restar(self, producto):
        id = str(producto.id)
        if id in self.carrito:
            self.carrito[id]["cantidad"] -= 1
            self.carrito[id]["total"] = str(float(self.carrito[id]["precio"]) * self.carrito[id]["cantidad"])
            if self.carrito[id]["cantidad"] <= 0:
                self.eliminar(producto)
            self.guardar_carrito()
            
    def limpiar(self): 
        self.session["carrito"] = {}
        self.session.modified = True