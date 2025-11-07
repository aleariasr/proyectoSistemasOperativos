import socket
import json

def conectar_servidor(ip_servidor, puerto=5050):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((ip_servidor, puerto))
        print(f"[CONECTADO] Servidor {ip_servidor}:{puerto}")
        return cliente
    except Exception as e:
        print(f"[ERROR] No se pudo conectar al servidor: {e}")
        return None

def enviar_comandos(cliente):
    try:
        while True:
            mensaje = input("Cliente > ").strip()
            if not mensaje:
                continue

            cliente.send(mensaje.encode('utf-8'))
            respuesta = cliente.recv(4096).decode('utf-8')

            # Si la respuesta parece ser JSON, formatearla
            try:
                data = json.loads(respuesta)
                print("\n=== Información del Sistema ===")
                for k, v in data.items():
                    print(f"{k}: {v}")
                print("==============================\n")
            except json.JSONDecodeError:
                print(f"Servidor > {respuesta}")

            if mensaje.lower() == "salir":
                break

    except KeyboardInterrupt:
        print("\n[INTERRUPCIÓN MANUAL] Cerrando conexión...")
    finally:
        cliente.close()
        print("[DESCONECTADO DEL SERVIDOR]")