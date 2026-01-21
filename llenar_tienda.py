import os
import django
from django.db import transaction

# 1. Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from store.models import Producto, Categoria


def generar_catalogo():
    """Devuelve un diccionario con categorías y productos para poblar la BD."""
    return {
        "Smartphones": [
            {"nombre": "iPhone 15 Pro", "precio": 1200.50, "img": "https://images.unsplash.com/photo-1695048132832-b41495f12eb4?q=80&w=1170&auto=format&fit=crop"},
            {"nombre": "Samsung Galaxy S24", "precio": 899, "img": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?q=80&w=500&auto=format&fit=crop"},
            {"nombre": "Google Pixel 8", "precio": 799, "img": "https://i.blogs.es/adefd2/pixel-8-16/1200_800.jpeg"},
            {"nombre": "Xiaomi 14", "precio": 749, "img": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=500&auto=format&fit=crop"},
            {"nombre": "OnePlus 12", "precio": 829, "img": "https://i.blogs.es/bb6fea/img_2639/1200_900.jpeg"},
        ],

        "Laptops": [
            {"nombre": "MacBook Air M3", "precio": 1200, "img": "https://www.apple.com/newsroom/images/2024/03/apple-unveils-the-new-13-and-15-inch-macbook-air-with-the-powerful-m3-chip/tile/Apple-MacBook-Air-2-up-hero-240304-lp.jpg.landing-big_2x.jpg"},
            {"nombre": "Dell XPS 13", "precio": 1100, "img": "https://platform.theverge.com/wp-content/uploads/sites/2/chorus/hermano/verge/product/image/10098/236524_Dell_XPS_13_AKrales_0016.jpg?quality=90&strip=all&crop=0,0,100,100"},
            {"nombre": "HP Spectre x360", "precio": 1250, "img": "https://images-cdn.ubuy.co.in/63628697e9c3fe717f171e0c-new-2018-hp-spectre-x360-2-in-1.jpg"},
            {"nombre": "Lenovo ThinkPad X1", "precio": 1350, "img": "https://i.blogs.es/c1d50e/lenovotpx1ap/1366_2000.jpg"},
            {"nombre": "Asus ZenBook 14", "precio": 999, "img": "https://dlcdnwebimgs.asus.com/gain/838fbdac-6d10-4190-8e52-d4b9463f5d23/"},
        ],

        "Audio": [
            {"nombre": "Sony WH-1000XM5", "precio": 350, "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=500&auto=format&fit=crop"},
            {"nombre": "Bose QuietComfort Ultra", "precio": 399, "img": "https://i.ebayimg.com/00/s/MTYwMFgxNjAw/z/yooAAOSw4oBnovV5/$_57.JPG"},
            {"nombre": "JBL Tune 770NC", "precio": 180, "img": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?q=80&w=500&auto=format&fit=crop"},
            {"nombre": "Apple AirPods Pro", "precio": 249, "img": "https://cdsassets.apple.com/live/SZLF0YNV/images/sp/111851_sp880-airpods-Pro-2nd-gen.png"},
        ],

        "Accesorios": [
            {"nombre": "Mouse Logitech MX Master 3", "precio": 130, "img": "https://nomadaware.com.ec/wp-content/uploads/NomadaWare_mouse_Logitech_MX_Master_3S_color.png"},
            {"nombre": "Teclado Mecánico Keychron K6", "precio": 89, "img": "https://images-na.ssl-images-amazon.com/images/I/51BZiJqxybS.jpg"},
            {"nombre": "Monitor LG UltraWide 34\"", "precio": 499, "img": "https://www.lg.com/ec/images/monitores/md07548280/gallery/Dm-1.jpg"},
            {"nombre": "Cargador Anker 65W", "precio": 59, "img": "https://m.media-amazon.com/images/I/61Thha4PJBL.jpg"},
            {"nombre": "Soporte para Laptop", "precio": 39, "img": "https://http2.mlstatic.com/D_NQ_NP_832076-MEC46650723083_072021-O.webp"},
            {"nombre": "Hub USB-C 7 en 1", "precio": 69, "img": "https://nomadaware.com.ec/wp-content/uploads/NomadaWare_nitron_hub_usb_c_7_en_1.webp"},
        ],

        # Nuevas categorías sugeridas
        "Consolas": [
            {"nombre": "PlayStation 5 SLIM", "precio": 499, "img": "https://ecsonyb2c.vtexassets.com/arquivos/ids/253644/711719570820_004.jpg?v=638478236755100000"},
            {"nombre": "Xbox Series X", "precio": 499, "img": "https://i.blogs.es/0aee46/xboxxapfinal/1200_900.jpg"},
            {"nombre": "Nintendo Switch OLED", "precio": 349, "img": "https://megamaxi-225de.kxcdn.com/wp-content/uploads/2024/12/45496597368-1-11.jpg"},
            {"nombre": "Steam Deck", "precio": 399, "img": "https://cdn.akamai.steamstatic.com/steamdeck/images/video/overview_oled.jpg"},
        ],

        "Videojuegos": [
            {"nombre": "The Legend of Zelda: Tears of the Kingdom", "precio": 59, "img": "https://zeldacentral.com/wp-content/uploads/2025/03/Tears-of-the-Kingdom-wallpaper.jpg"},
            {"nombre": "Elden Ring - Deluxe Edition", "precio": 49, "img": "https://image.api.playstation.com/vulcan/ap/rnd/202402/0817/7c785de020c1a28cb8bb606abe1a1e95eaf2030abfda111f.png"},
            {"nombre": "FC26 - Standard Edition", "precio": 59, "img": "https://image.api.playstation.com/vulcan/ap/rnd/202507/1617/2e757ffb0a6bb4b91af84db64e0183d725e56e5354f45eba.png"},
        ],

        "Ropa": [
            {"nombre": "Camiseta Gamer - Logo Retro", "precio": 25, "img": "https://images-na.ssl-images-amazon.com/images/I/715opmOGyOL._AC_UL600_SR600,600_.jpg"},
            {"nombre": "Sudadera con capucha", "precio": 45, "img": "https://m.media-amazon.com/images/I/71oZfgQ4jIL._AC_UL1500_.jpg"},
            {"nombre": "Gorra Snapback", "precio": 20, "img": "https://neweraec.vtexassets.com/arquivos/ids/159398/11591024_1.jpg?v=638324730231570000"},
        ],

        "Accesorios Gaming": [
            {"nombre": "Gamepad inalámbrico Pro ThunderRobot", "precio": 59, "img": "https://nomadaware.com.ec/wp-content/uploads/NomadaWare_gamepad_Thunderobot_G40_Dual_Shock-500x500.webp"},
            {"nombre": "Auriculares Gaming con micrófono", "precio": 89, "img": "https://images.unsplash.com/photo-1545727210-2f6d3f4a9f3b?q=80&w=1170&auto=format&fit=crop"},
            {"nombre": "Silla COOLER MASTER CALIBER E1", "precio": 199, "img": "https://nomadaware.com.ec/wp-content/uploads/NomadaWare_silla_cooler_master_caliber_e1_purple-500x500.webp"},
        ],

        "Juegos de Mesa": [
            {"nombre": "Dungeons & Dragons - Starter Set", "precio": 69.99, "img": "https://m.media-amazon.com/images/I/91wX2UeUZHL._AC_SL1500_.jpg"},
        ],
    }


@transaction.atomic
def poblar():
    catalogo = generar_catalogo()

    print("--- Limpiando base de datos ---")
    Producto.objects.all().delete()
    Categoria.objects.all().delete()

    total_productos = 0

    for nombre_cat, productos in catalogo.items():
        cat_obj, created = Categoria.objects.get_or_create(nombre=nombre_cat)
        if created:
            print(f"Categoria creada: {nombre_cat}")

        for p in productos:
            Producto.objects.create(
                categoria=cat_obj,
                nombre=p["nombre"],
                descripcion=f"Edición especial de {p['nombre']} disponible en I-BEY.",
                precio=p["precio"],
                stock=15,
                imagen=p["img"],
            )
            total_productos += 1
            print(f"Cargado: {p['nombre']} (categoria: {nombre_cat})")

    print(f"DATOS CARGADOS EXITOSAMENTE: {total_productos} productos en {len(catalogo)} categorías")


if __name__ == '__main__':
    poblar()
