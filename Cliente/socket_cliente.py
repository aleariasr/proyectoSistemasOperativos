import socket
import json

RECV_SIZE = 4096

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

            # PROTOCOLO CORRECTO: el servidor procesa por líneas con '\n'
            cliente.sendall((mensaje + "\n").encode("utf-8"))

            # Recibir respuesta (puede ser texto o cabecera IMG)
            data = cliente.recv(RECV_SIZE)
            if not data:
                print("[DESCONECTADO] El servidor cerró la conexión.")
                break

            # Si es cabecera de imagen: "IMG <bytes>\n" + payload binario
            if data.startswith(b"IMG "):
                # separar cabecera y lo que ya vino de payload (si vino algo)
                header, _, tail = data.partition(b"\n")
                try:
                    _, size_str = header.decode("utf-8", errors="replace").split(" ", 1)
                    size = int(size_str)
                except Exception:
                    print("Cabecera de imagen inválida:", header)
                    continue

                # ya pudo venir parte del PNG en 'tail'
                png = bytearray(tail)
                while len(png) < size:
                    chunk = cliente.recv(min(RECV_SIZE, size - len(png)))
                    if not chunk:
                        print("Conexión cerrada recibiendo imagen")
                        break
                    png.extend(chunk)

                if len(png) == size:
                    with open("captura.png", "wb") as f:
                        f.write(png)
                    print(f"✅ Captura guardada como captura.png ({size} bytes)")
                continue

            # Texto/JSON normal
            texto = data.decode("utf-8", errors="replace").strip()
            # El servidor manda '\n' al final; puede venir más de una línea
            for linea in texto.splitlines():
                linea = linea.strip()
                if not linea:
                    continue
                # intentar formatear JSON bonito si aplica
                try:
                    obj = json.loads(linea)
                    print("\n=== Información del Sistema ===")
                    for k, v in obj.items():
                        print(f"{k}: {v}")
                    print("===============================\n")
                except json.JSONDecodeError:
                    print(f"Servidor > {linea}")

            if mensaje.lower() == "salir":
                break

    except KeyboardInterrupt:
        print("\n[INTERRUPCIÓN] Cerrando conexión...")
    finally:
        try:
            cliente.close()
        except Exception:
            pass
        print("[DESCONECTADO DEL SERVIDOR]")