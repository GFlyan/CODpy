from pynput.mouse import Listener
import vgamepad as vg
import threading
import pyautogui
import math
import time

# Controle virtual Xbox 360
gamepad = vg.VX360Gamepad()

# Configurações de suavidade
scale = 0.03
deadzone = 0.01
smooth_factor = 0.85
last_x, last_y = None, None
smoothed_dx, smoothed_dy = 0.0, 0.0

# Aim assist simulado
target_x, target_y = pyautogui.size()[0] // 2, pyautogui.size()[1] // 2  # alvo no centro
aim_radius = 150
assist_strength = 0.12


def move_analog(delta_x, delta_y):
    global smoothed_dx, smoothed_dy

    # Suavização
    smoothed_dx = (smooth_factor * smoothed_dx) + ((1 - smooth_factor) * delta_x)
    smoothed_dy = (smooth_factor * smoothed_dy) + ((1 - smooth_factor) * delta_y)

    # Aim assist: atrai para o centro se estiver perto
    mouse_x, mouse_y = pyautogui.position()
    distance = math.hypot(target_x - mouse_x, target_y - mouse_y)

    if distance < aim_radius:
        pull_x = (target_x - mouse_x) * assist_strength
        pull_y = (target_y - mouse_y) * assist_strength
        smoothed_dx += pull_x
        smoothed_dy += pull_y

    # Aplica escala
    x = max(min(smoothed_dx * scale, 1.0), -1.0)
    y = max(min(-smoothed_dy * scale, 1.0), -1.0)

    # Zona morta
    if abs(x) < deadzone: x = 0.0
    if abs(y) < deadzone: y = 0.0

    # Atualiza controle
    gamepad.right_joystick_float(x_value_float=x, y_value_float=y)
    gamepad.update()


def on_move(x, y):
    global last_x, last_y

    if last_x is None or last_y is None:
        last_x, last_y = x, y
        return

    delta_x = x - last_x
    delta_y = y - last_y
    last_x, last_y = x, y

    if abs(delta_x) > 100 or abs(delta_y) > 100:
        return

    move_analog(delta_x, delta_y)


def start_listener():
    with Listener(on_move=on_move) as listener:
        listener.join()


# Inicia listener
threading.Thread(target=start_listener, daemon=True).start()
print("🎯 Aim Assist + controle suave ativado!")
input("Pressione Enter para encerrar...\n")
