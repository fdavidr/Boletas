"""
Script para crear un logo de ejemplo para BOLETAS-V1
Genera un logo simple con las iniciales de la empresa
"""

from PIL import Image, ImageDraw, ImageFont
import os

def crear_logo(
    texto="BP",
    color_fondo=(52, 73, 94),
    color_texto=(255, 255, 255),
    tamano=(200, 200),
    nombre_archivo="logo.png"
):
    """
    Crea un logo simple con texto centrado
    
    Args:
        texto: Texto a mostrar (generalmente iniciales)
        color_fondo: Color de fondo en RGB
        color_texto: Color del texto en RGB
        tamano: Tupla (ancho, alto) del logo
        nombre_archivo: Nombre del archivo a guardar
    """
    # Crear la imagen
    img = Image.new('RGB', tamano, color_fondo)
    draw = ImageDraw.Draw(img)
    
    # Intentar usar una fuente del sistema, si no usar la predeterminada
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    # Calcular posición del texto para centrarlo
    bbox = draw.textbbox((0, 0), texto, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (tamano[0] - text_width) // 2
    y = (tamano[1] - text_height) // 2 - 10
    
    # Dibujar el texto
    draw.text((x, y), texto, fill=color_texto, font=font)
    
    # Crear directorio si no existe
    directorio = os.path.join('static', 'uploads')
    os.makedirs(directorio, exist_ok=True)
    
    # Guardar la imagen
    ruta_completa = os.path.join(directorio, nombre_archivo)
    img.save(ruta_completa)
    print(f"✅ Logo creado exitosamente: {ruta_completa}")
    return ruta_completa

if __name__ == "__main__":
    # Crear logo por defecto
    crear_logo()
    
    print("\n📝 Si desea crear un logo personalizado, puede ejecutar:")
    print("   python crear_logo.py")
    print("   Y modificar los parámetros en la función crear_logo()")
