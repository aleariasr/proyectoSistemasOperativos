import socket
import json
import threading
import io
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import messagebox
from mouse_cliente import controlar_mouse_remoto
from threading import Event

# =========================
# Configuración de estilo
# =========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # base; coloreamos acentos nosotros

PRIMARY = "#4F46E5"   # Indigo-600
PRIMARY_DARK = "#3730A3"
ACCENT = "#14B8A6"    # Teal-500
BG = "#0F172A"        # Slate-900
CARD = "#111827"      # Gray-900
TEXT_MUTED = "#94A3B8"

# =========================
# Cliente TCP no bloqueante
# =========================
class RemoteClient:
    RECV = 4096
    def __init__(self):
        self.sock: socket.socket | None = None
        self.lock = threading.Lock()

    def connect(self, host: str, port: int = 5050):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        self.sock = s

    def close(self):
        with self.lock:
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass
                self.sock = None

    def is_connected(self) -> bool:
        return self.sock is not None

    def send_line(self, line: str) -> bytes:
        """
        Envía una línea (terminada en \n) y devuelve los bytes crudos de respuesta
        (puede ser texto o cabecera IMG + payload). Se usa de forma sincrónica
        dentro de un thread de trabajo para no congelar la GUI.
        """
        with self.lock:
            if not self.sock:
                raise ConnectionError("No conectado")
            self.sock.sendall((line + "\n").encode("utf-8"))
            data = self.sock.recv(self.RECV)
            if not data:
                raise ConnectionError("Conexión cerrada por el servidor")
            # Si la respuesta es imagen: "IMG <bytes>\n" + payload
            if data.startswith(b"IMG "):
                header, _, tail = data.partition(b"\n")
                _, size_str = header.decode("utf-8", "replace").split(" ", 1)
                size = int(size_str)
                buf = bytearray(tail)
                while len(buf) < size:
                    chunk = self.sock.recv(min(self.RECV, size - len(buf)))
                    if not chunk:
                        break
                    buf.extend(chunk)
                return b"IMG\n" + bytes(buf)  # marcamos con cabecera simple propia
            return data

# =========================
# GUI
# =========================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IF4001 - Control Remoto (Cliente)")
        self.geometry("1100x700")
        self.configure(fg_color=BG)

        self.client = RemoteClient()
        self.mouse_stop = Event()
        self.mouse_thread: threading.Thread | None = None
        self.screenshot_imgtk = None  # para mantener referencia
        self.pulse_up = True
        self.pulse_alpha = 0.25

        self._build_layout()
        self._animate_header()

    # ------------- UI Layout -------------
    def _build_layout(self):
        # Grid base
        self.grid_columnconfigure(0, weight=0)  # sidebar
        self.grid_columnconfigure(1, weight=1)  # content
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, corner_radius=20, fg_color=CARD)
        self.sidebar.grid(row=0, column=0, padx=16, pady=16, sticky="ns")
        self.sidebar.grid_rowconfigure(99, weight=1)

        self.header = ctk.CTkLabel(self.sidebar, text="Remote Controller",
                                   font=ctk.CTkFont(size=20, weight="bold"),
                                   text_color="white")
        self.header.grid(row=0, column=0, padx=16, pady=(16, 6), sticky="w")

        self.subheader = ctk.CTkLabel(self.sidebar, text="Cliente TCP",
                                      font=ctk.CTkFont(size=13),
                                      text_color=TEXT_MUTED)
        self.subheader.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

        # Conexión
        self.ip_entry = ctk.CTkEntry(self.sidebar, placeholder_text="IP del servidor",
                                     width=230, corner_radius=12)
        self.ip_entry.grid(row=2, column=0, padx=16, pady=6)

        self.port_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Puerto (5050)",
                                       width=230, corner_radius=12)
        self.port_entry.insert(0, "5050")
        self.port_entry.grid(row=3, column=0, padx=16, pady=6)

        self.connect_btn = ctk.CTkButton(self.sidebar, text="Conectar",
                                         command=self._on_connect_click,
                                         fg_color=PRIMARY, hover_color=PRIMARY_DARK,
                                         corner_radius=14, height=40)
        self.connect_btn.grid(row=4, column=0, padx=16, pady=(6, 12), sticky="ew")

        self.status = ctk.CTkLabel(self.sidebar, text="Desconectado",
                                   text_color="#F87171")  # red-400
        self.status.grid(row=5, column=0, padx=16, pady=(0, 16), sticky="w")

        self.sep = ctk.CTkFrame(self.sidebar, height=2, fg_color="#1F2937")
        self.sep.grid(row=6, column=0, sticky="ew", padx=16, pady=8)

        # Acciones
        self.info_btn = ctk.CTkButton(self.sidebar, text="Info del sistema",
                                      command=self._cmd_info, corner_radius=12,
                                      fg_color=ACCENT, hover_color="#0D9488")
        self.info_btn.grid(row=7, column=0, padx=16, pady=6, sticky="ew")

        self.ss_btn = ctk.CTkButton(self.sidebar, text="Captura de pantalla",
                                    command=self._cmd_screenshot, corner_radius=12)
        self.ss_btn.grid(row=8, column=0, padx=16, pady=6, sticky="ew")

        self.msg_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Mensaje al remoto",
                                      width=230, corner_radius=12)
        self.msg_entry.grid(row=9, column=0, padx=16, pady=(12, 6))
        self.msg_btn = ctk.CTkButton(self.sidebar, text="Enviar mensaje",
                                     command=self._cmd_message, corner_radius=12)
        self.msg_btn.grid(row=10, column=0, padx=16, pady=6, sticky="ew")

        self.sep2 = ctk.CTkFrame(self.sidebar, height=2, fg_color="#1F2937")
        self.sep2.grid(row=11, column=0, sticky="ew", padx=16, pady=8)

        self.mouse_toggle = ctk.CTkSwitch(self.sidebar, text="Controlar ratón",
                                          command=self._toggle_mouse, onvalue="on", offvalue="off")
        self.mouse_toggle.grid(row=12, column=0, padx=16, pady=(6, 6), sticky="w")

        self.vol_row = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.vol_row.grid(row=13, column=0, padx=16, pady=(8, 6), sticky="ew")
        self.vol_row.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(self.vol_row, text="Vol +", command=self._cmd_vol_up, corner_radius=10, height=32).grid(row=0, column=0, padx=4)
        ctk.CTkButton(self.vol_row, text="Mute",  command=self._cmd_vol_mute, corner_radius=10, height=32).grid(row=0, column=1, padx=4)
        ctk.CTkButton(self.vol_row, text="Vol -", command=self._cmd_vol_down, corner_radius=10, height=32).grid(row=0, column=2, padx=4)

        self.power_row = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.power_row.grid(row=14, column=0, padx=16, pady=(6, 16), sticky="ew")
        self.power_row.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(self.power_row, text="Apagar",    command=self._cmd_power_off,  fg_color="#DC2626", hover_color="#B91C1C", corner_radius=10, height=32).grid(row=0, column=0, padx=4)
        ctk.CTkButton(self.power_row, text="Reiniciar", command=self._cmd_reboot,     fg_color="#EA580C", hover_color="#C2410C", corner_radius=10, height=32).grid(row=0, column=1, padx=4)
        ctk.CTkButton(self.power_row, text="Cerrar Ses.", command=self._cmd_logout,   fg_color="#9333EA", hover_color="#7E22CE", corner_radius=10, height=32).grid(row=0, column=2, padx=4)

        # Panel principal (tabs)
        self.content = ctk.CTkTabview(self, corner_radius=16,
                                      segmented_button_fg_color=PRIMARY_DARK,
                                      segmented_button_selected_color=PRIMARY,
                                      segmented_button_unselected_color="#1F2937")
        self.content.grid(row=0, column=1, padx=16, pady=16, sticky="nsew")

        self.tab_info = self.content.add("Información")
        self.tab_screen = self.content.add("Captura")
        self.tab_log = self.content.add("Log")

        # Info
        self.info_text = ctk.CTkTextbox(self.tab_info, corner_radius=14, fg_color="#0B1220", text_color="#E5E7EB")
        self.info_text.pack(expand=True, fill="both", padx=12, pady=12)

        # Captura
        self.screen_frame = ctk.CTkFrame(self.tab_screen, corner_radius=14, fg_color="#0B1220")
        self.screen_frame.pack(expand=True, fill="both", padx=12, pady=12)
        self.screen_label = ctk.CTkLabel(self.screen_frame, text="(Sin captura aún)")
        self.screen_label.pack(pady=20)

        # Log
        self.log_text = ctk.CTkTextbox(self.tab_log, corner_radius=14, fg_color="#0B1220", text_color="#CBD5E1")
        self.log_text.pack(expand=True, fill="both", padx=12, pady=12)

    # ------------- Animación sutil del header -------------
    def _animate_header(self):
        # Pulso suave en el color del título
        try:
            a = self.pulse_alpha
            col = self._blend(PRIMARY, "white", a)
            self.header.configure(text_color=col)
            if self.pulse_up:
                self.pulse_alpha += 0.02
                if self.pulse_alpha >= 0.55:
                    self.pulse_up = False
            else:
                self.pulse_alpha -= 0.02
                if self.pulse_alpha <= 0.20:
                    self.pulse_up = True
        except Exception:
            pass
        self.after(50, self._animate_header)

    def _blend(self, c1, c2, t):
        # c1, c2 = "#RRGGBB"
        def hex_to_rgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
        def rgb_to_hex(r,g,b): return "#{:02X}{:02X}{:02X}".format(r,g,b)
        r1,g1,b1 = hex_to_rgb(c1)
        r2,g2,b2 = hex_to_rgb(c2)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return rgb_to_hex(r,g,b)

    # ------------- Helpers UI -------------
    def _set_status(self, text: str, ok: bool):
        self.status.configure(text=text, text_color=("#34D399" if ok else "#F87171"))

    def _append_log(self, text: str):
        self.log_text.insert("end", text.rstrip() + "\n")
        self.log_text.see("end")

    def _safe_thread(self, target, *args):
        t = threading.Thread(target=target, args=args, daemon=True)
        t.start()
        return t

    # ------------- Acciones de conexión -------------
    def _on_connect_click(self):
        if not self.client.is_connected():
            host = self.ip_entry.get().strip()
            if not host:
                messagebox.showwarning("Aviso", "Ingresa la IP del servidor.")
                return
            try:
                port = int(self.port_entry.get().strip() or "5050")
            except ValueError:
                messagebox.showwarning("Aviso", "Puerto inválido.")
                return

            def work():
                try:
                    self.client.connect(host, port)
                    self._set_status("Conectado", True)
                    self.connect_btn.configure(text="Desconectar", fg_color="#EF4444", hover_color="#DC2626")
                    self._append_log(f"[OK] Conectado a {host}:{port}")
                    # decirle al servidor que vamos a usar modo mouse si toca
                except Exception as e:
                    self._append_log(f"[ERR] {e}")
                    messagebox.showerror("Error", str(e))

            self._safe_thread(work)
        else:
            # Desconectar
            def work():
                try:
                    self._stop_mouse_if_running()
                    self.client.close()
                    self._set_status("Desconectado", False)
                    self.connect_btn.configure(text="Conectar", fg_color=PRIMARY, hover_color=PRIMARY_DARK)
                    self._append_log("[OK] Desconectado")
                except Exception as e:
                    self._append_log(f"[ERR] {e}")
            self._safe_thread(work)

    # ------------- Comandos primarios -------------
    def _cmd_info(self):
        if not self.client.is_connected():
            return messagebox.showinfo("Info", "Conéctate primero.")
        def work():
            try:
                data = self.client.send_line("INFO_SISTEMA")
                text = data.decode("utf-8", "replace").strip()
                # Puede venir varias líneas; tomamos línea por línea JSON válida
                pretty = []
                for line in text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        pretty.append(json.dumps(obj, indent=2, ensure_ascii=False))
                    except json.JSONDecodeError:
                        pretty.append(line)
                out = "\n".join(pretty)
                self.info_text.delete("1.0", "end")
                self.info_text.insert("1.0", out)
                self.content.set("Información")
                self._append_log("[OK] INFO_SISTEMA")
            except Exception as e:
                self._append_log(f"[ERR] {e}")
        self._safe_thread(work)

    def _cmd_screenshot(self):
        if not self.client.is_connected():
            return messagebox.showinfo("Info", "Conéctate primero.")
        def work():
            try:
                raw = self.client.send_line("SCREENSHOT")
                if raw.startswith(b"IMG\n"):
                    png = raw.split(b"\n", 1)[1]
                    img = Image.open(io.BytesIO(png))
                    # ajustar a tamaño del panel manteniendo aspecto
                    w = self.screen_frame.winfo_width() or 800
                    h = self.screen_frame.winfo_height() or 500
                    img.thumbnail((w-40, h-40))
                    self.screenshot_imgtk = ImageTk.PhotoImage(img)
                    self.screen_label.configure(image=self.screenshot_imgtk, text="")
                    self.content.set("Captura")
                    self._append_log("[OK] SCREENSHOT")
                else:
                    self._append_log("[ERR] Respuesta inesperada de SCREENSHOT")
            except Exception as e:
                self._append_log(f"[ERR] {e}")
        self._safe_thread(work)

    def _cmd_message(self):
        if not self.client.is_connected():
            return messagebox.showinfo("Info", "Conéctate primero.")
        txt = self.msg_entry.get().strip()
        if not txt:
            return
        def work():
            try:
                resp = self.client.send_line(f"MENSAJE {txt}").decode("utf-8", "replace").strip()
                self._append_log(f"[MENSAJE] {resp}")
            except Exception as e:
                self._append_log(f"[ERR] {e}")
        self._safe_thread(work)

    # ------------- Volumen / Energía -------------
    def _cmd_vol_up(self):     self._simple_cmd("VOLUMEN_SUBIR")
    def _cmd_vol_down(self):   self._simple_cmd("VOLUMEN_BAJAR")
    def _cmd_vol_mute(self):   self._simple_cmd("VOLUMEN_MUTE")
    def _cmd_power_off(self):  self._confirm_cmd("APAGAR", "¿Apagar el equipo remoto?")
    def _cmd_reboot(self):     self._confirm_cmd("REINICIAR", "¿Reiniciar el equipo remoto?")
    def _cmd_logout(self):     self._confirm_cmd("CERRAR_SESION", "¿Cerrar la sesión del usuario remoto?")

    def _simple_cmd(self, cmd: str):
        if not self.client.is_connected():
            return messagebox.showinfo("Info", "Conéctate primero.")
        def work():
            try:
                resp = self.client.send_line(cmd).decode("utf-8","replace").strip()
                self._append_log(f"[{cmd}] {resp}")
            except Exception as e:
                self._append_log(f"[ERR] {e}")
        self._safe_thread(work)

    def _confirm_cmd(self, cmd: str, question: str):
        if not self.client.is_connected():
            return messagebox.showinfo("Info", "Conéctate primero.")
        if not messagebox.askyesno("Confirmar", question):
            return
        self._simple_cmd(cmd)

    # ------------- Mouse remoto -------------
    def _toggle_mouse(self):
        if not self.client.is_connected():
            messagebox.showinfo("Info", "Conéctate primero.")
            self.mouse_toggle.deselect()
            return
        if self.mouse_toggle.get() == "on":
            # Aviso al servidor (opcional, solo para limpiar el “no reconocido”)
            def work_start():
                try:
                    try:
                        self.client.send_line("CONTROL_MOUSE")
                    except Exception:
                        pass
                    self.mouse_stop.clear()
                    self.mouse_thread = threading.Thread(
                        target=controlar_mouse_remoto,
                        args=(self.client.sock, self.mouse_stop, 30),
                        daemon=True
                    )
                    self.mouse_thread.start()
                    self._append_log("[MOUSE] control remoto ACTIVADO")
                except Exception as e:
                    self._append_log(f"[ERR] {e}")
                    self.mouse_toggle.deselect()
            self._safe_thread(work_start)
        else:
            self._stop_mouse_if_running()

    def _stop_mouse_if_running(self):
        if self.mouse_thread and self.mouse_thread.is_alive():
            self.mouse_stop.set()
            self.mouse_thread.join(timeout=1.0)
            self._append_log("[MOUSE] control remoto DESACTIVADO")


if __name__ == "__main__":
    app = App()
    app.mainloop()