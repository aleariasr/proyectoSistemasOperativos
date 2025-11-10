import platform
import psutil
import os
import socket
import json
import getpass
from datetime import datetime

def obtener_informacion_sistema():
    """
    Obtiene información del sistema remoto y la devuelve como JSON (str).
    """
    # Información básica
    try:
        usuario = getpass.getuser()
    except Exception:
        try:
            usuario = os.getlogin()
        except Exception:
            usuario = "desconocido"

    info = {
        "nombre_so": platform.system(),
        "version_so": platform.version(),
        "plataforma": platform.platform(),
        "nombre_equipo": socket.gethostname(),
        "procesador": platform.processor() or "N/D",
        "usuario_actual": usuario,
        "zona_horaria": datetime.now().astimezone().tzname(),
        "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # RAM total
    try:
        ram = psutil.virtual_memory()
        info["ram_total_gb"] = round(ram.total / (1024 ** 3), 2)
    except Exception:
        info["ram_total_gb"] = None

    # Discos
    discos = []
    try:
        for particion in psutil.disk_partitions(all=False):
            try:
                uso = psutil.disk_usage(particion.mountpoint)
                discos.append({
                    "unidad": particion.device,
                    "formato": particion.fstype,
                    "tamaño_total_gb": round(uso.total / (1024 ** 3), 2),
                    "usado_gb": round(uso.used / (1024 ** 3), 2),
                    "libre_gb": round(uso.free / (1024 ** 3), 2)
                })
            except PermissionError:
                continue
    except Exception:
        pass
    info["discos"] = discos

    # Procesos (top 10 por nombre)
    procesos = []
    try:
        for p in psutil.process_iter(['pid', 'name']):
            procesos.append({"pid": p.info.get('pid'), "nombre": p.info.get('name')})
    except Exception:
        pass
    info["procesos"] = procesos[:10]

    return json.dumps(info, ensure_ascii=False)