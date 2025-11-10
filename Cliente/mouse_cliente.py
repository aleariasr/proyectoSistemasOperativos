import socket
import time
from pynput import mouse

def controlar_mouse_remoto(cliente):
    """
    Envía en tiempo real los movimientos y clics del mouse al servidor.
    Presiona Ctrl+C para detener.
    """
    print("🖱️ Control remoto activado. Mueve el mouse o haz clic. Ctrl+C para salir.")

    def on_move(x, y):
        try:
            cliente.sendall(f"MOUSE_MOVE {int(x)} {int(y)}\n".encode('utf-8'))
        except Exception:
            return False  # detiene el listener

    def on_click(x, y, button, pressed):
        if pressed:
            btn = str(button).split(".")[-1]
            if btn == "left":
                cliente.sendall(b"MOUSE_CLICK_IZQ\n")
            elif btn == "right":
                cliente.sendall(b"MOUSE_CLICK_DER\n")

    with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("🛑 Control remoto detenido.")