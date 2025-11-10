import pyautogui

def mover_cursor(x, y):
    """Mueve el cursor a las coordenadas dadas."""
    try:
        pyautogui.moveTo(x, y, duration=0.0)
        return f"Cursor movido a ({x}, {y})"
    except Exception as e:
        return f"Error al mover el cursor: {e}"

def click_izquierdo():
    """Hace clic izquierdo."""
    try:
        pyautogui.click(button='left')
        return "Clic izquierdo ejecutado"
    except Exception as e:
        return f"Error al hacer clic izquierdo: {e}"

def click_derecho():
    """Hace clic derecho."""
    try:
        pyautogui.click(button='right')
        return "Clic derecho ejecutado"
    except Exception as e:
        return f"Error al hacer clic derecho: {e}"

def doble_click():
    """Hace doble clic."""
    try:
        pyautogui.doubleClick()
        return "Doble clic ejecutado"
    except Exception as e:
        return f"Error al hacer doble clic: {e}"