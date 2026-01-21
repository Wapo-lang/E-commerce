from .models import Categoria

def menu_categorias(request):
    # Retorna un diccionario con todas las categorías para usar en el navbar
    return {'categorias_menu': Categoria.objects.all()}