import os
import platform
import subprocess
import ctypes

def subir_volumen():
    sistema = platform.system()
    try:
        if sistema == "Windows":
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            dispositivos = AudioUtilities.GetSpeakers()
            interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
            volumen.VolumeStepUp(None)
        elif sistema == "Darwin":  # macOS
            os.system("osascript -e 'set volume output volume ((output volume of (get volume settings)) + 10)'")
        return "Volumen aumentado"
    except Exception as e:
        return f"Error al subir volumen: {e}"

def bajar_volumen():
    sistema = platform.system()
    try:
        if sistema == "Windows":
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            dispositivos = AudioUtilities.GetSpeakers()
            interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
            volumen.VolumeStepDown(None)
        elif sistema == "Darwin":
            os.system("osascript -e 'set volume output volume ((output volume of (get volume settings)) - 10)'")
        return "Volumen reducido"
    except Exception as e:
        return f"Error al bajar volumen: {e}"

def silenciar():
    sistema = platform.system()
    try:
        if sistema == "Windows":
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            dispositivos = AudioUtilities.GetSpeakers()
            interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volumen = cast(interfaz, POINTER(IAudioEndpointVolume))
            volumen.SetMute(1, None)
        elif sistema == "Darwin":
            os.system("osascript -e 'set volume output muted true'")
        return "Sonido silenciado"
    except Exception as e:
        return f"Error al silenciar: {e}"

def apagar():
    sistema = platform.system()
    try:
        if sistema == "Windows":
            os.system("shutdown /s /t 0")
        elif sistema == "Darwin":
            os.system("osascript -e 'tell app \"System Events\" to shut down'")
        elif sistema == "Linux":
            os.system("shutdown now")
        return "Apagando el equipo..."
    except Exception as e:
        return f"Error al apagar: {e}"

def reiniciar():
    sistema = platform.system()
    try:
        if sistema == "Windows":
            os.system("shutdown /r /t 0")
        elif sistema == "Darwin":
            os.system("osascript -e 'tell app \"System Events\" to restart'")
        elif sistema == "Linux":
            os.system("reboot")
        return "Reiniciando el equipo..."
    except Exception as e:
        return f"Error al reiniciar: {e}"

def cerrar_sesion():
    sistema = platform.system()
    try:
        if sistema == "Windows":
            os.system("shutdown /l")
        elif sistema == "Darwin":
            os.system("osascript -e 'tell app \"System Events\" to log out'")
        return "Cerrando sesión..."
    except Exception as e:
        return f"Error al cerrar sesión: {e}"

def mostrar_mensaje(texto="Mensaje remoto"):
    """Muestra una ventana emergente con un mensaje."""
    try:
        if platform.system() == "Windows":
            ctypes.windll.user32.MessageBoxW(0, texto, "Mensaje del Controlador", 1)
        else:
            os.system(f"osascript -e 'display dialog \"{texto}\" with title \"Mensaje del Controlador\"'")
        return "Mensaje mostrado correctamente"
    except Exception as e:
        return f"Error al mostrar mensaje: {e}"