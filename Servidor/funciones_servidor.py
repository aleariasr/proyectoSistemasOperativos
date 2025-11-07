import platform
import psutil
import os
import socket
import json
from datetime import datetime

def obtener_informacion_sistema():
    """Obtiene información detallada del sistema remoto y la devuelve como JSON."""

    # Información básica del sistema
    info = {
        "nombre_so": platform.system(),
        "version_so": platform.version(),
        "plataforma": platform.platform(),
        "nombre_equipo": socket.gethostname(),
        "procesador": platform.processor(),
        "usuario_actual": os.getlogin(),
        "zona_horaria": datetime.now().astimezone().tzname(),
        "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # RAM total
    ram = psutil.virtual_memory()
    info["ram_total_gb"] = round(ram.total / (1024 ** 3), 2)

    # Discos
    discos = []
    for particion in psutil.disk_partitions():
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
    info["discos"] = discos

    # Procesos
    procesos = []
    for p in psutil.process_iter(['pid', 'name']):
        procesos.append({"pid": p.info['pid'], "nombre": p.info['name']})
    info["procesos"] = procesos[:10]  # solo primeros 10 para no saturar

    return json.dumps(info)