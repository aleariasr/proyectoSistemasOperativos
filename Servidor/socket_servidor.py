import socket
import threading
from screenshot_servidor import capturar_pantalla_png_bytes #para las funciones de captura pantalla
from funciones_servidor import obtener_informacion_sistema
from control_sistema import (
    subir_volumen, bajar_volumen, silenciar,
    apagar, reiniciar, cerrar_sesion, mostrar_mensaje
)
from control_mouse import mover_cursor, click_izquierdo, click_derecho, doble_click
from typing import Union

HOST = ''          # 0.0.0.0 en todas las interfaces
PORT = 5050
RECV_SIZE = 4096   # mayor por si vienen líneas largas
IDLE_TIMEOUT = 120 # segs por conexión

def _procesar_comando(cmd: str) -> Union[str, bytes]:
    comando = cmd.strip()
    comando_upper = comando.upper()

    if not comando:
        return ""

    if comando_upper == "SALIR":
        return "__CLOSE__"
    if comando_upper == "INFO_SISTEMA":
        return obtener_informacion_sistema()
    if comando_upper == "VOLUMEN_SUBIR":
        return subir_volumen()
    if comando_upper == "VOLUMEN_BAJAR":
        return bajar_volumen()
    if comando_upper == "VOLUMEN_MUTE":
        return silenciar()
    if comando_upper == "APAGAR":
        return apagar()
    if comando_upper == "REINICIAR":
        return reiniciar()
    if comando_upper == "CERRAR_SESION":
        return cerrar_sesion()
    if comando_upper.startswith("MENSAJE "):
        texto = comando[len("MENSAJE "):]
        return mostrar_mensaje(texto)
    if comando_upper == "SCREENSHOT":
        try:
            return capturar_pantalla_png_bytes()  #  bytes PNG
        except Exception as e:
            return f"Error al capturar pantalla: {e}"
        
    if comando_upper.startswith("MOUSE_MOVE"):
        # formato: MOUSE_MOVE x y
        try:
            _, x_str, y_str = comando.split()
            x, y = int(x_str), int(y_str)
            return mover_cursor(x, y)
        except Exception:
            return "Uso: MOUSE_MOVE <x> <y>"

    if comando_upper == "MOUSE_CLICK_IZQ":
        return click_izquierdo()

    if comando_upper == "MOUSE_CLICK_DER":
        return click_derecho()

    if comando_upper == "MOUSE_DBLCLICK":
        return doble_click()
    
    if comando_upper == "CONTROL_MOUSE":
        return "Modo de control de ratón activado (cliente enviará eventos)."
    
    return f"Comando no reconocido: {comando}"


def manejar_cliente(conn: socket.socket, addr):
    print(f"[NUEVA CONEXIÓN] {addr} conectado.")
    conn.settimeout(IDLE_TIMEOUT)
    buffer = ""

    try:
        while True:
            chunk = conn.recv(RECV_SIZE)
            if not chunk:
                break
            buffer += chunk.decode('utf-8', errors='replace')

            # Procesa por líneas completas
            while '\n' in buffer:
                linea, buffer = buffer.split('\n', 1)
                respuesta = _procesar_comando(linea)

                if respuesta == "":
                    continue
                if respuesta == "__CLOSE__":
                    conn.sendall("Conexión cerrada por el cliente.\n".encode('utf-8'))
                    return

                # detectar si la respuesta es bytes para la captura de pantalla (imagen PNG) ---
                if isinstance(respuesta, (bytes, bytearray)):
                    n = len(respuesta)
                    # Enviar encabezado con tamaño de imagen
                    conn.sendall(f"IMG {n}\n".encode("utf-8"))
                    # Enviar los bytes del PNG
                    conn.sendall(respuesta)
                else:
                    # Respuesta de texto normal
                    conn.sendall((respuesta + "\n").encode('utf-8'))
                # ---------------------------------------------------------------

    except socket.timeout:
        conn.sendall("Timeout de inactividad.\n".encode('utf-8'))
    except Exception as e:
        try:
            conn.sendall((f"[ERROR] {e}\n").encode('utf-8'))
        except Exception:
            pass
        print(f"[ERROR] {addr}: {e}")
    finally:
        conn.close()
        print(f"[DESCONECTADO] {addr}")


def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[ESCUCHANDO] Servidor activo en puerto {PORT}")

    try:
        while True:
            conn, addr = server.accept()
            hilo = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
            hilo.start()
            print(f"[CONEXIONES ACTIVAS] {threading.active_count() - 1}")
    finally:
        server.close()
