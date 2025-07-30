from pynput.mouse import Listener
import vgamepad as vg
import threading
import pyautogui
import math
import time

gamepad = vg.VX360Gamepad()

# Parâmetros derivados do documento
scaleFactorX = 200
scaleFactorY = 400
smoothing = 0.9             # escala de suavização (interpreta 9 como 0.9)
noiseFilter = 0.02          # zona morta ampliada (baseado em filtro de ruído)
assist_strength = 0.2
aim_radius = 200

screen_width, screen_height = pyautogui.size()
target_x, target_y = screen_width // 2, screen_height // 2

last_x, last_y = None, None
smoothed_dx, smoothed_dy = 0.0, 0.0
last_move_time = time.time()

def apply_curve(value, axis='x'):
    # Simula os pontos da curva descrita no arquivo (padrão parabólica leve)
    curve_points = [(0.0, 0.0), (0.4, 0.6), (0.7, 0.9), (1.0, 1.0)]
    abs_val = abs(value)
    for i in range(len(curve_points) - 1):
        p1, p2 = curve_points[i], curve_points[i+1]
        if abs_val <= p2[0]:
            ratio = (abs_val - p1[0]) / (p2[0] - p1[0])
            curved = p1[1] + ratio * (p2[1] - p1[1])
            return math.copysign(curved, value)
    return math.copysign(1.0, value)

def move_analog(delta_x, delta_y):
    global smoothed_dx, smoothed_dy, last_move_time

    last_move_time = time.time()

    smoothed_dx = (smoothing * smoothed_dx) + ((1 - smoothing) * delta_x)
    smoothed_dy = (smoothing * smoothed_dy) + ((1 - smoothing) * delta_y)

    mouse_x, mouse_y = pyautogui.position()
    dist = math.hypot(target_x - mouse_x, target_y - mouse_y)

    if dist < aim_radius:
        dx_assist = (target_x - mouse_x) * assist_strength
        dy_assist = (target_y - mouse_y) * assist_strength
        smoothed_dx += dx_assist
        smoothed_dy += dy_assist

    # Aplica escala e curva de resposta
    x_raw = smoothed_dx / screen_width * scaleFactorX
    y_raw = smoothed_dy / screen_height * scaleFactorY

    x = apply_curve(x_raw)
    y = apply_curve(y_raw)

    if abs(x) < noiseFilter: x = 0.0
    if abs(y) < noiseFilter: y = 0.0

    gamepad.right_joystick_float(x_value_float=max(min(x, 1.0), -1.0),
                                 y_value_float=max(min(y, 1.0), -1.0))
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

def start_listener():
    listener = Listener(on_move=on_move)
    listener.start()
    listener.join()

# Threads paralelas
threading.Thread(target=reset_analog_if_idle, daemon=True).start()
threading.Thread(target=start_listener, daemon=True).start()

print("🎮 Analógico virtual calibrado com curva Vortex e aim assist suave.")
input("Pressione Enter para encerrar...\n")
