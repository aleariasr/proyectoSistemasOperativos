import os
import platform
import subprocess
import ctypes


def _is_windows():
    return platform.system() == "Windows"


def _is_macos():
    return platform.system() == "Darwin"


def _applescript(cmd: str) -> int:
    # Ejecuta AppleScript y devuelve el código de salida
    return os.system(f"osascript -e '{cmd}'")


def subir_volumen():
    try:
        if _is_windows():
            # Usar pyautogui - más simple y confiable
            import pyautogui
            # Simular presionar tecla de subir volumen 3 veces
            for _ in range(3):
                pyautogui.press('volumeup')
            return "Volumen aumentado"
        elif _is_macos():
            _applescript("set v to output volume of (get volume settings)")
            _applescript("set nv to (v + 10)")
            _applescript("if nv > 100 then set nv to 100")
            _applescript("set volume output volume nv")
            return "Volumen aumentado"
        else:
            return "Volumen: acción no implementada en este SO"
    except Exception as e:
        return f"Error al subir volumen: {e}"


def bajar_volumen():
    try:
        if _is_windows():
            # Usar pyautogui - más simple y confiable
            import pyautogui
            # Simular presionar tecla de bajar volumen 3 veces
            for _ in range(3):
                pyautogui.press('volumedown')
            return "Volumen reducido"
        elif _is_macos():
            _applescript("set v to output volume of (get volume settings)")
            _applescript("set nv to (v - 10)")
            _applescript("if nv < 0 then set nv to 0")
            _applescript("set volume output volume nv")
            return "Volumen reducido"
        else:
            return "Volumen: acción no implementada en este SO"
    except Exception as e:
        return f"Error al bajar volumen: {e}"


def silenciar():
    try:
        if _is_windows():
            # Usar pyautogui - más simple y confiable
            import pyautogui
            pyautogui.press('volumemute')
            return "Sonido silenciado/activado"
        elif _is_macos():
            _applescript("set volume output muted true")
            return "Sonido silenciado"
        else:
            return "Silencio: acción no implementada en este SO"
    except Exception as e:
        return f"Error al silenciar: {e}"


def apagar():
    try:
        if _is_windows():
            os.system("shutdown /s /t 0")
        elif _is_macos():
            _applescript('tell app "System Events" to shut down')
        else:  # Linux
            ret = os.system("shutdown -h now")
            if ret != 0:
                return "Error: requiere privilegios (sudo) para apagar en Linux"
        return "Apagando el equipo..."
    except Exception as e:
        return f"Error al apagar: {e}"


def reiniciar():
    try:
        if _is_windows():
            os.system("shutdown /r /t 0")
        elif _is_macos():
            _applescript('tell app "System Events" to restart')
        else:  # Linux
            ret = os.system("reboot")
            if ret != 0:
                return "Error: requiere privilegios (sudo) para reiniciar en Linux"
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
            return "Cerrar sesión: acción no implementada en este SO"
        return "Cerrando sesión..."
    except Exception as e:
        return f"Error al cerrar sesión: {e}"


def mostrar_mensaje(texto="Mensaje remoto"):
    """Muestra una ventana emergente con un mensaje."""
    try:
        if _is_windows():
            ctypes.windll.user32.MessageBoxW(
                0, str(texto), "Mensaje del Controlador", 1
            )
        elif _is_macos():
            # Escapar comillas para AppleScript
            safe = str(texto).replace('"', '\\"')
            _applescript(
                f'display dialog "{safe}" with title "Mensaje del Controlador"'
            )
        else:
            return "Mostrar mensaje: acción no implementada en este SO"
        return "Mensaje mostrado correctamente"
    except Exception as e:
        return f"Error al mostrar mensaje: {e}"