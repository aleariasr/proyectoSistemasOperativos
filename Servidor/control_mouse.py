import pyautogui

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
    except Exception as e:
        return f"Error al hacer clic izquierdo: {e}"
    return ""

def click_derecho():
    try:
        pyautogui.click(button='right')
    except Exception as e:
        return f"Error al hacer clic derecho: {e}"
    return ""

def doble_click():
    try:
        pyautogui.doubleClick()
    except Exception as e:
        return f"Error al hacer doble clic: {e}"
    return ""