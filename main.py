from pynput.mouse import Listener
import vgamepad as vg
import threading
import pyautogui
import math
import time

gamepad = vg.VX360Gamepad()

scale = 0.03
deadzone = 0.01
smooth_factor = 0.85
assist_strength = 0.15
aim_radius = 200

screen_width, screen_height = pyautogui.size()
target_x, target_y = screen_width // 2, screen_height // 2

last_x, last_y = None, None
smoothed_dx, smoothed_dy = 0.0, 0.0
last_move_time = time.time()

def move_analog(delta_x, delta_y):
    global smoothed_dx, smoothed_dy, last_move_time

    last_move_time = time.time()

    smoothed_dx = (smooth_factor * smoothed_dx) + ((1 - smooth_factor) * delta_x)
    smoothed_dy = (smooth_factor * smoothed_dy) + ((1 - smooth_factor) * delta_y)

    mouse_x, mouse_y = pyautogui.position()
    dist = math.hypot(target_x - mouse_x, target_y - mouse_y)

    if dist < aim_radius:
        dx_assist = (target_x - mouse_x) * assist_strength
        dy_assist = (target_y - mouse_y) * assist_strength
        smoothed_dx += dx_assist
        smoothed_dy += dy_assist

    # Corrigido: sem inversão no eixo X
    x = max(min(smoothed_dx * scale, 1.0), -1.0)
    y = max(min(smoothed_dy * scale, 1.0), -1.0)

    if abs(x) < deadzone: x = 0.0
    if abs(y) < deadzone: y = 0.0

    gamepad.right_joystick_float(x_value_float=x, y_value_float=y)
    gamepad.update()

def reset_analog_if_idle():
    global smoothed_dx, smoothed_dy
    while True:
        if time.time() - last_move_time > 0.2:
            smoothed_dx = 0.0
            smoothed_dy = 0.0
            gamepad.right_joystick_float(x_value_float=0.0, y_value_float=0.0)
            gamepad.update()
        time.sleep(0.05)

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

threading.Thread(target=reset_analog_if_idle, daemon=True).start()
threading.Thread(target=lambda: Listener(on_move=on_move).join(), daemon=True).start()

print("🎮 Analógico virtual está calibrado e responsivo!")
input("Pressione Enter para encerrar...\n")
