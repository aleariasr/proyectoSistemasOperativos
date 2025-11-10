# Cliente/mouse_cliente.py
import time
from pynput import mouse

def controlar_mouse_remoto(cliente):
    """
    Envía los movimientos y clics del mouse al servidor con límite de frecuencia.
    Ctrl+C para detener.
    """
    print("🖱️ Control remoto activado. Mueve el mouse o haz clic. Ctrl+C para salir.")

    ultimo_envio = 0
    intervalo = 0.03  # segundos entre envíos (≈33 ms → 30 fps)

    def on_move(x, y):
        nonlocal ultimo_envio
        ahora = time.time()
        if ahora - ultimo_envio >= intervalo:
            try:
                cliente.sendall(f"MOUSE_MOVE {int(x)} {int(y)}\n".encode("utf-8"))
                ultimo_envio = ahora
            except Exception:
                return False  # detiene listener

    def on_click(x, y, button, pressed):
        if pressed:
            try:
                btn = str(button).split(".")[-1]
                if btn == "left":
                    cliente.sendall(b"MOUSE_CLICK_IZQ\n")
                elif btn == "right":
                    cliente.sendall(b"MOUSE_CLICK_DER\n")
            except Exception:
                return False

    with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("🛑 Control remoto detenido.")