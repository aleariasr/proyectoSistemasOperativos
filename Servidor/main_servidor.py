from socket_servidor import iniciar_servidor

if __name__ == "__main__":
    print("=== Servidor TCP - Sistemas Operativos ===")
    try:
        iniciar_servidor()
    except KeyboardInterrupt:
        print("\n[DETENIDO] Servidor finalizado manualmente.")
    except Exception as e:
        print(f"[ERROR CRÍTICO] {e}")
