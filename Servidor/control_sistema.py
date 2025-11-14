def _set_volume_macos(delta: int):
    script = f'''
    set v to output volume of (get volume settings)
    set nv to v + {delta}
    if nv > 100 then set nv to 100
    if nv < 0 then set nv to 0
    set volume output volume nv
    return nv
    '''
    ret = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return ret.stdout.strip()

import os
import platform
import subprocess
import ctypes


def _is_windows():
    return platform.system() == "Windows"


def _is_macos():
    return platform.system() == "Darwin"


def _applescript(cmd: str) -> int:
    return os.system(f"osascript -e '{cmd}'")


def _set_volume_macos(delta: int):
    script = f'''
    set v to output volume of (get volume settings)
    set nv to v + {delta}
    if nv > 100 then set nv to 100
    if nv < 0 then set nv to 0
    set volume output volume nv
    return nv
    '''
    ret = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return ret.stdout.strip()


# ───────────────────────────────────────────────
#                  VOLUMEN
# ───────────────────────────────────────────────

def subir_volumen():
    try:
        if _is_windows():
            try:
                # Intentar con pycaw (más profesional)
                from ctypes import POINTER, cast
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))

                current = volume.GetMasterVolumeLevelScalar()
                new = min(current + 0.10, 1.0)
                volume.SetMasterVolumeLevelScalar(new, None)
                return f"Volumen aumentado a {int(new * 100)}%"

            except Exception:
                # Fallback con pyautogui si pycaw no existe
                import pyautogui
                for _ in range(3):
                    pyautogui.press("volumeup")
                return "Volumen aumentado (pyautogui)"

        elif _is_macos():
            nuevo = _set_volume_macos(+10)
            return f"Volumen aumentado a {nuevo}%"

        else:
            return "Volumen: no implementado para este SO"
    except Exception as e:
        return f"Error al subir volumen: {e}"


def bajar_volumen():
    try:
        if _is_windows():
            try:
                # Intentar con pycaw
                from ctypes import POINTER, cast
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))

                current = volume.GetMasterVolumeLevelScalar()
                new = max(current - 0.10, 0.0)
                volume.SetMasterVolumeLevelScalar(new, None)
                return f"Volumen reducido a {int(new * 100)}%"

            except Exception:
                # Fallback
                import pyautogui
                for _ in range(3):
                    pyautogui.press("volumedown")
                return "Volumen reducido (pyautogui)"

        elif _is_macos():
            nuevo = _set_volume_macos(-10)
            return f"Volumen reducido a {nuevo}%"

        else:
            return "Volumen: no implementado para este SO"
    except Exception as e:
        return f"Error al bajar volumen: {e}"


def silenciar():
    try:
        if _is_windows():
            import pyautogui
            pyautogui.press("volumemute")
            return "Sonido silenciado/activado"

        elif _is_macos():
            _applescript("set volume output muted true")
            return "Sonido silenciado"

        else:
            return "Silencio: no implementado en este SO"
    except Exception as e:
        return f"Error al silenciar: {e}"


# ───────────────────────────────────────────────
#             APAGAR / REINICIAR / LOGOUT
# ───────────────────────────────────────────────

def apagar():
    try:
        if _is_windows():
            os.system("shutdown /s /t 0")

        elif _is_macos():
            _applescript('tell app "System Events" to shut down')

        else:
            return "Apagar: no implementado"

        return "Apagando el equipo..."
    except Exception as e:
        return f"Error al apagar: {e}"


def reiniciar():
    try:
        if _is_windows():
            os.system("shutdown /r /t 0")

        elif _is_macos():
            _applescript('tell app "System Events" to restart')

        else:
            return "Reiniciar: no implementado"

        return "Reiniciando el equipo..."
    except Exception as e:
        return f"Error al reiniciar: {e}"


def cerrar_sesion():
    try:
        if _is_windows():
            os.system("shutdown /l")

        elif _is_macos():
            _applescript('tell app "System Events" to log out')

        else:
            return "Cerrar sesión: no implementado"

        return "Cerrando sesión..."
    except Exception as e:
        return f"Error al cerrar sesión: {e}"


# ───────────────────────────────────────────────
#               MOSTRAR MENSAJE
# ───────────────────────────────────────────────

def mostrar_mensaje(texto="Mensaje remoto"):
    try:
        if _is_windows():
            ctypes.windll.user32.MessageBoxW(0, str(texto), "Mensaje del Controlador", 1)

        elif _is_macos():
            safe = str(texto).replace('"', '\\"')
            _applescript(f'display dialog "{safe}" with title "Mensaje del Controlador"')

        else:
            return "Mostrar mensaje: no implementado"

        return "Mensaje mostrado correctamente"
    except Exception as e:
        return f"Error al mostrar mensaje: {e}"