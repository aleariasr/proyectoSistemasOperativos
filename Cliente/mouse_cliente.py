# Cliente/mouse_cliente.py
import time
from threading import Event
from pynput import mouse

def controlar_mouse_remoto(cliente, stop_event: Event, fps: int = 30):
    """
    Envía movimientos y clics del mouse al servidor con límite de frecuencia (fps).
    Se detiene cuando stop_event.is_set() == True.
    """
    intervalo = 1.0 / max(1, fps)
    ultimo_envio = 0.0

    def on_move(x, y):
        nonlocal ultimo_envio
        if stop_event.is_set():
            return False
        ahora = time.time()
        if (ahora - ultimo_envio) >= intervalo:
            try:
                cliente.sendall(f"MOUSE_MOVE {int(x)} {int(y)}\n".encode("utf-8"))
                ultimo_envio = ahora
            except Exception:
                return False

    def on_click(x, y, button, pressed):
        if stop_event.is_set():
            return False
        if pressed:
            try:
                btn = str(button).split(".")[-1]
                if btn == "left":
                    cliente.sendall(b"MOUSE_CLICK_IZQ\n")
                elif btn == "right":
                    cliente.sendall(b"MOUSE_CLICK_DER\n")
            except Exception:
                return False

    listener = mouse.Listener(on_move=on_move, on_click=on_click)
    listener.start()
    try:
        while listener.is_alive() and not stop_event.is_set():
            time.sleep(0.05)
    finally:
        try:
            listener.stop()
        except Exception:
            pass