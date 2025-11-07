import socket
import threading
from funciones_servidor import obtener_informacion_sistema

HOST = ''
PORT = 5050

def manejar_cliente(conn, addr):
    print(f"[NUEVA CONEXIÓN] {addr} conectado.")
    try:
        while True:
            data = conn.recv(2048).decode('utf-8')
            if not data:
                break

            comando = data.strip().upper()
            print(f"[{addr}] Comando recibido: {comando}")

            if comando == "SALIR":
                conn.send("Conexión cerrada por el cliente.".encode('utf-8'))
                break

            elif comando == "INFO_SISTEMA":
                respuesta = obtener_informacion_sistema()

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