import socket
import threading
import customtkinter as ctk
from datetime import datetime
from screenshot_servidor import capturar_pantalla_png_bytes
from funciones_servidor import obtener_informacion_sistema
from control_sistema import (
    subir_volumen, bajar_volumen, silenciar,
    apagar, reiniciar, cerrar_sesion, mostrar_mensaje
)
from control_mouse import mover_cursor, click_izquierdo, click_derecho, doble_click
from typing import Union

# =========================
# Configuración de estilo (igual que el cliente)
# =========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PRIMARY = "#4F46E5"
PRIMARY_DARK = "#3730A3"
ACCENT = "#14B8A6"
BG = "#0F172A"
CARD = "#111827"
TEXT_MUTED = "#94A3B8"
SUCCESS = "#34D399"
ERROR = "#F87171"

# =========================
# Configuración del servidor
# =========================
HOST = ''
PORT = 5050
RECV_SIZE = 4096
IDLE_TIMEOUT = 120


class ServidorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("IF4001 - Servidor Remoto")
        self.geometry("700x600")
        self.configure(fg_color=BG)
        
        # Variables del servidor
        self.servidor_socket = None
        self.servidor_activo = False
        self.clientes_conectados = {}  # {addr: conn}
        
        self._build_ui()
        self._iniciar_servidor()
        
    def _build_ui(self):
        """Construye la interfaz gráfica"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color=CARD)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="🖥️ Servidor de Control Remoto",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        self.title_label.pack(anchor="w")
        
        self.subtitle = ctk.CTkLabel(
            header_frame,
            text="Sistema Operativos - Equipo Remoto",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        )
        self.subtitle.pack(anchor="w", pady=(5, 0))
        
        # Separador
        sep1 = ctk.CTkFrame(self.main_frame, height=2, fg_color="#1F2937")
        sep1.pack(fill="x", padx=20, pady=15)
        
        # Estado de conexión
        estado_frame = ctk.CTkFrame(self.main_frame, fg_color="#0B1220", corner_radius=12)
        estado_frame.pack(fill="x", padx=20, pady=10)
        
        # Indicador visual de estado
        self.status_indicator = ctk.CTkFrame(
            estado_frame,
            width=12,
            height=12,
            corner_radius=6,
            fg_color=ERROR
        )
        self.status_indicator.pack(side="left", padx=(15, 10), pady=15)
        
        status_text_frame = ctk.CTkFrame(estado_frame, fg_color="transparent")
        status_text_frame.pack(side="left", fill="x", expand=True, pady=15)
        
        self.status_label = ctk.CTkLabel(
            status_text_frame,
            text="Esperando conexión...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ERROR,
            anchor="w"
        )
        self.status_label.pack(anchor="w")
        
        self.ip_label = ctk.CTkLabel(
            status_text_frame,
            text=f"IP del servidor: {self._obtener_ip_local()} | Puerto: {PORT}",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
            anchor="w"
        )
        self.ip_label.pack(anchor="w", pady=(5, 0))
        
        # Información de clientes
        info_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=10)
        
        self.clients_label = ctk.CTkLabel(
            info_frame,
            text="Clientes conectados: 0",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED,
            anchor="w"
        )
        self.clients_label.pack(anchor="w")
        
        # Separador
        sep2 = ctk.CTkFrame(self.main_frame, height=2, fg_color="#1F2937")
        sep2.pack(fill="x", padx=20, pady=15)
        
        # Log de actividad
        log_header = ctk.CTkLabel(
            self.main_frame,
            text="📋 Log de Actividad",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
            anchor="w"
        )
        log_header.pack(anchor="w", padx=20, pady=(0, 10))
        
        self.log_text = ctk.CTkTextbox(
            self.main_frame,
            corner_radius=12,
            fg_color="#0B1220",
            text_color="#E5E7EB",
            font=ctk.CTkFont(size=11, family="Consolas")
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Agregar mensaje inicial
        self._log(f"✓ Servidor iniciado en puerto {PORT}")
        self._log(f"✓ Esperando conexiones en {self._obtener_ip_local()}:{PORT}")
    
    def _obtener_ip_local(self) -> str:
        """Obtiene la IP local de la máquina"""
        try:
            # Truco: conectarse a un servidor externo para obtener la IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def _log(self, mensaje: str):
        """Agrega un mensaje al log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {mensaje}\n")
        self.log_text.see("end")
    
    def _actualizar_estado(self, conectado: bool, ip_cliente: str = ""):
        """Actualiza el indicador visual de estado"""
        if conectado:
            self.status_indicator.configure(fg_color=SUCCESS)
            self.status_label.configure(
                text=f"🟢 Conectado a {ip_cliente}",
                text_color=SUCCESS
            )
        else:
            self.status_indicator.configure(fg_color=ERROR)
            self.status_label.configure(
                text="🔴 Esperando conexión...",
                text_color=ERROR
            )
    
    def _actualizar_contador_clientes(self):
        """Actualiza el contador de clientes conectados"""
        count = len(self.clientes_conectados)
        self.clients_label.configure(text=f"Clientes conectados: {count}")
    
    def _iniciar_servidor(self):
        """Inicia el servidor en un thread separado"""
        thread = threading.Thread(target=self._run_servidor, daemon=True)
        thread.start()
    
    def _run_servidor(self):
        """Lógica principal del servidor"""
        try:
            self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.servidor_socket.bind((HOST, PORT))
            self.servidor_socket.listen(5)
            self.servidor_activo = True
            
            while self.servidor_activo:
                try:
                    conn, addr = self.servidor_socket.accept()
                    self.clientes_conectados[addr] = conn
                    
                    # Actualizar UI
                    self.after(0, lambda: self._actualizar_estado(True, f"{addr[0]}:{addr[1]}"))
                    self.after(0, self._actualizar_contador_clientes)
                    self.after(0, lambda: self._log(f"✓ Cliente conectado: {addr[0]}:{addr[1]}"))
                    
                    # Crear thread para manejar el cliente
                    thread = threading.Thread(
                        target=self._manejar_cliente,
                        args=(conn, addr),
                        daemon=True
                    )
                    thread.start()
                    
                except OSError:
                    break
                    
        except Exception as e:
            self.after(0, lambda: self._log(f"✗ Error al iniciar servidor: {e}"))
    
    def _manejar_cliente(self, conn: socket.socket, addr):
        """Maneja la comunicación con un cliente (basado en socket_servidor.py)"""
        conn.settimeout(IDLE_TIMEOUT)
        buffer = ""
        
        try:
            while True:
                chunk = conn.recv(RECV_SIZE)
                if not chunk:
                    break
                buffer += chunk.decode('utf-8', errors='replace')
                
                while '\n' in buffer:
                    linea, buffer = buffer.split('\n', 1)
                    
                    # Log del comando recibido
                    self.after(0, lambda cmd=linea: self._log(f"← {addr[0]}: {cmd}"))
                    
                    respuesta = self._procesar_comando(linea)
                    
                    if respuesta == "":
                        continue
                    if respuesta == "__CLOSE__":
                        conn.sendall("Conexión cerrada por el cliente.\n".encode('utf-8'))
                        return
                    
                    # Enviar respuesta
                    if isinstance(respuesta, (bytes, bytearray)):
                        n = len(respuesta)
                        conn.sendall(f"IMG {n}\n".encode("utf-8"))
                        conn.sendall(respuesta)
                        self.after(0, lambda: self._log(f"→ {addr[0]}: Imagen enviada ({n} bytes)"))
                    else:
                        conn.sendall((respuesta + "\n").encode('utf-8'))
                        # Log de respuesta (truncada si es muy larga)
                        resp_preview = respuesta[:50] + "..." if len(respuesta) > 50 else respuesta
                        self.after(0, lambda r=resp_preview: self._log(f"→ {addr[0]}: {r}"))
        
        except socket.timeout:
            conn.sendall("Timeout de inactividad.\n".encode('utf-8'))
            self.after(0, lambda: self._log(f"⚠ Timeout: {addr[0]}"))
        except Exception as e:
            self.after(0, lambda: self._log(f"✗ Error con {addr[0]}: {e}"))
        finally:
            conn.close()
            if addr in self.clientes_conectados:
                del self.clientes_conectados[addr]
            
            self.after(0, self._actualizar_contador_clientes)
            self.after(0, lambda: self._log(f"✗ Cliente desconectado: {addr[0]}:{addr[1]}"))
            
            # Si no hay más clientes, volver a estado de espera
            if len(self.clientes_conectados) == 0:
                self.after(0, lambda: self._actualizar_estado(False))
    
    def _procesar_comando(self, cmd: str) -> Union[str, bytes]:
        """Procesa los comandos recibidos (copiado de socket_servidor.py)"""
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
                return capturar_pantalla_png_bytes()
            except Exception as e:
                return f"Error al capturar pantalla: {e}"
        
        if comando_upper.startswith("MOUSE_MOVE"):
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
    
    def on_closing(self):
        """Maneja el cierre de la ventana"""
        self.servidor_activo = False
        if self.servidor_socket:
            self.servidor_socket.close()
        self.destroy()


if __name__ == "__main__":
    app = ServidorGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()