from io import BytesIO
import mss
from PIL import Image

def capturar_pantalla_png_bytes(region=None):
    """
    Captura la pantalla (o una región) y devuelve los bytes PNG.
    region = (left, top, width, height) o None para pantalla completa.
    """
    with mss.mss() as sct:
        if region is None:
            monitor = sct.monitors[1]  # pantalla principal
        else:
            l, t, w, h = region
            monitor = {"left": l, "top": t, "width": w, "height": h}

        raw = sct.grab(monitor)
        img = Image.frombytes("RGB", raw.size, raw.rgb)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
