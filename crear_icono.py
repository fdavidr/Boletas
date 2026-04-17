"""
Genera boletas.ico — icono de la aplicación Boletas V1.
Requiere Pillow (ya incluido en requirements.txt).
"""

from PIL import Image, ImageDraw, ImageFont
import os

def crear_icono(destino: str = 'boletas.ico'):
    sizes = [16, 24, 32, 48, 64, 128, 256]
    frames = []

    for s in sizes:
        img  = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Fondo azul oscuro con esquinas redondeadas
        m = max(1, s // 10)
        draw.rounded_rectangle(
            [m, m, s - m - 1, s - m - 1],
            radius=max(2, s // 5),
            fill=(44, 62, 80, 255)          # #2c3e50
        )

        # Borde sutil
        draw.rounded_rectangle(
            [m, m, s - m - 1, s - m - 1],
            radius=max(2, s // 5),
            outline=(52, 152, 219, 200),    # #3498db
            width=max(1, s // 24)
        )

        # Letra "B" centrada en blanco
        font_size = max(6, int(s * 0.52))
        font = None
        for nombre_fuente in ('arialbd.ttf', 'arial.ttf', 'DejaVuSans-Bold.ttf'):
            try:
                font = ImageFont.truetype(nombre_fuente, font_size)
                break
            except Exception:
                pass
        if font is None:
            font = ImageFont.load_default()

        bbox  = draw.textbbox((0, 0), 'B', font=font)
        tw    = bbox[2] - bbox[0]
        th    = bbox[3] - bbox[1]
        tx    = (s - tw) // 2 - bbox[0]
        ty    = (s - th) // 2 - bbox[1]
        draw.text((tx, ty), 'B', fill=(255, 255, 255, 255), font=font)

        frames.append(img)

    frames[0].save(
        destino,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=frames[1:]
    )
    print(f'Icono guardado en: {destino}')


if __name__ == '__main__':
    crear_icono()
