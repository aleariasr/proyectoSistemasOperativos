# Cliente/test_screenshot.py
import socket
import sys

HOST = "127.0.0.1"   # Cambia por la IP del servidor si es remoto
PORT = 5050

def recv_line(sock: socket.socket) -> str:
    """Lee hasta '\n' (incluye multi-reads) y devuelve la línea sin el salto."""
    data = b""
    while True:
        ch = sock.recv(1)
        if not ch:
            # conexión cerrada sin fin de línea
            raise ConnectionError("Conexión cerrada leyendo cabecera")
        if ch == b"\n":
            break
        data += ch
    return data.decode("utf-8", errors="replace")

def recv_exact(sock: socket.socket, n: int) -> bytes:
    """Lee exactamente n bytes o lanza error si la conexión se cierra antes."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Conexión cerrada leyendo payload")
        buf += chunk
    return buf

def main():
    # Permite pasar HOST y PORT por argumentos opcionales
    # Ej: python test_screenshot.py 192.168.1.50 5050
    host = HOST
    port = PORT
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        # Enviar comando por línea (tu servidor lo espera con '\n')
        s.sendall(b"SCREENSHOT\n")

        # 1) leer cabecera tipo: "IMG <bytes>\n" o un mensaje de texto
        header = recv_line(s).strip()

        # Si la respuesta no empieza con IMG, es un texto (error o mensaje)
        if not header.startswith("IMG "):
            print("Respuesta del servidor:", header)
            return

        # 2) parsear tamaño y leer exactamente ese número de bytes PNG
        try:
            _, size_str = header.split(" ", 1)
            size = int(size_str)
        except Exception:
            print("Cabecera inválida:", header)
            return

        png_data = recv_exact(s, size)

    # 3) guardar el PNG
    out_name = "captura.png"
    with open(out_name, "wb") as f:
        f.write(png_data)

    print(f"✅ Captura guardada como {out_name} ({len(png_data)} bytes)")

if __name__ == "__main__":
    main()
