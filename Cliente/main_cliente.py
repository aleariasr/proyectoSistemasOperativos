from socket_cliente import conectar_servidor, enviar_comandos

if __name__ == "__main__":
    print("=== Cliente TCP (persistente) - Sistemas Operativos ===")
    ip = input("Ingrese la IP del servidor: ").strip()
    cliente = conectar_servidor(ip)
    if cliente:
        enviar_comandos(cliente)