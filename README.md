# Proyecto Final IF4001 – Sistemas Operativos

## Control Remoto de Equipo mediante Sockets TCP/IP

### Segundo Semestre 2025

---

## 1. Información General del Proyecto

Este proyecto implementa dos aplicaciones en Python que permiten controlar un equipo remoto mediante sockets TCP/IP.  
El sistema consiste en:

- **Aplicación Servidor (Equipo Remoto)**  
  Escucha conexiones, ejecuta comandos y envía información del sistema o capturas de pantalla.

- **Aplicación Cliente (Equipo Controlador)**  
  Incluye una interfaz gráfica moderna (**customtkinter**) desde donde el usuario:
  - Se conecta al servidor por IP
  - Consulta información
  - Envía comandos
  - Ve capturas
  - Controla el mouse en tiempo real

---

## 2. Arquitectura del Proyecto

```
proyecto/
 ├── cliente/
 │   ├── gui_cliente.py
 │   ├── mouse_cliente.py
 │   └── test_screenshot.py
 │
 ├── servidor/
 │   ├── gui_servidor.py
 │   ├── socket_servidor.py
 │   ├── funciones_servidor.py
 │   ├── control_sistema.py
 │   ├── control_mouse.py
 │   └── screenshot_servidor.py
 │
 ├── requirements.txt
 └── README.md
```

Cada módulo tiene una única responsabilidad y mantiene el proyecto limpio y mantenible.

---

## 3. Protocolo de Comunicación TCP

La comunicación usa **líneas terminadas en `\n`**, lo que evita corrupción de datos.

### Comandos implementados:

```
INFO_SISTEMA
SCREENSHOT
MENSAJE <texto>
VOLUMEN_SUBIR
VOLUMEN_BAJAR
VOLUMEN_MUTE
APAGAR
REINICIAR
CERRAR_SESION
CONTROL_MOUSE
MOUSE_MOVE x y
MOUSE_CLICK_IZQ
MOUSE_CLICK_DER
MOUSE_DBLCLICK
```

### Respuestas del servidor:

- **Texto** → termina con `\n`
- **Imagen PNG** → formato:
  ```
  IMG <bytes>
  <payload PNG>
  ```

---

## 4. Funcionalidades Implementadas (100% rúbrica)

✔ Información completa del sistema  
✔ RAM total  
✔ Lista de discos (GB, libre, usado, formato)  
✔ Resolución pantalla  
✔ Usuario actual  
✔ Zona horaria  
✔ Fecha y hora  
✔ Procesos activos  
✔ Captura de pantalla  
✔ Enviar mensaje al remoto  
✔ Subir / bajar / silenciar volumen  
✔ Apagar / reiniciar / cerrar sesión  
✔ Control del mouse (movimiento + clic + doble clic)  
✔ Interfaz gráfica moderna  
✔ Logs  
✔ Manejo de errores  
✔ Multiplataforma (Windows y macOS)

---

## 5. Librerías Usadas

| Librería      | Propósito                     |
| ------------- | ----------------------------- |
| customtkinter | Interfaz moderna              |
| psutil        | RAM, discos, procesos         |
| mss           | Captura pantalla              |
| Pillow        | Procesar PNG                  |
| pyautogui     | Volumen (fallback), clics     |
| pynput        | Captura del mouse local       |
| pycaw         | Control de volumen en Windows |
| socket        | Protocolo TCP                 |
| threading     | Evitar bloqueos en GUI        |

---

## 6. Ejecución

### Instalar dependencias

```
pip install -r requirements.txt
```

### Servidor

GUI:

```
python3 servidor/gui_servidor.py
```

Sin GUI:

```
python3 servidor/socket_servidor.py
```

### Cliente

```
python3 cliente/gui_cliente.py
```

---

## 7. Manejo de Errores

El sistema maneja:

- Timeouts
- Reconexión segura
- Errores de AppleScript / pycaw
- Caídas del servidor
- Lectura parcial de buffers
- Locks para evitar condiciones de carrera
- Control de FPS del mouse para evitar lag
