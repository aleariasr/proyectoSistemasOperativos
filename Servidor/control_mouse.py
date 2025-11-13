import pyautogui

# Desactivar el fail-safe para control remoto
pyautogui.FAILSAFE = False

def mover_cursor(x, y):
    """Mueve el cursor a las coordenadas dadas."""
    try:
        pyautogui.moveTo(x, y, duration=0)
        return ""  # sin texto, evita lag
    except Exception as e:
        return f"Error al mover el cursor: {e}"

def click_izquierdo():
    try:
        pyautogui.click(button='left')
        return ""
    except Exception as e:
        return f"Error al hacer clic izquierdo: {e}"

def click_derecho():
    try:
        pyautogui.click(button='right')
        return ""
    except Exception as e:
        return f"Error al hacer clic derecho: {e}"

def doble_click():
    try:
        pyautogui.doubleClick()
        return ""
    except Exception as e:
        return f"Error al hacer doble clic: {e}"