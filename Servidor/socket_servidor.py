import socket
import threading
from funciones_servidor import obtener_informacion_sistema
from control_sistema import (
    subir_volumen, bajar_volumen, silenciar,
    apagar, reiniciar, cerrar_sesion, mostrar_mensaje
)

HOST = ''
PORT = 5050

def manejar_cliente(conn, addr):
    print(f"[NUEVA CONEXIÓN] {addr} conectado.")
    try:
        while True:
            data = conn.recv(2048).decode('utf-8')
            if not data:
                break

            comando = data.strip()
            comando_upper = comando.upper()
            print(f"[{addr}] Comando recibido: {comando}")

            if comando_upper == "SALIR":
                conn.send("Conexión cerrada por el cliente.".encode('utf-8'))
                break
            elif comando_upper == "INFO_SISTEMA":
                respuesta = obtener_informacion_sistema()
            elif comando_upper == "VOLUMEN_SUBIR":
                respuesta = subir_volumen()
            elif comando_upper == "VOLUMEN_BAJAR":
                respuesta = bajar_volumen()
            elif comando_upper == "VOLUMEN_MUTE":
                respuesta = silenciar()
            elif comando_upper == "APAGAR":
                respuesta = apagar()
            elif comando_upper == "REINICIAR":
                respuesta = reiniciar()
            elif comando_upper == "CERRAR_SESION":
                respuesta = cerrar_sesion()
            elif comando_upper.startswith("MENSAJE "):
                # extraemos el texto después del espacio
                texto = comando[len("MENSAJE "):]
                respuesta = mostrar_mensaje(texto)
            else:
                respuesta = f"Comando no reconocido: {comando}"

            conn.send(respuesta.encode('utf-8'))

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()
        print(f"[DESCONECTADO] {addr}")


def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[ESCUCHANDO] Servidor activo en puerto {PORT}")

    while True:
        conn, addr = server.accept()
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
        hilo.start()
        print(f"[CONEXIONES ACTIVAS] {threading.active_count() - 1}")