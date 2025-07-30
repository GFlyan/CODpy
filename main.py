from pynput.mouse import Listener
import vgamepad as vg
import threading
import time

# Inicializa controle virtual Xbox 360
gamepad = vg.VX360Gamepad()

# Configurações ajustadas
scale = 0.03            # Sensibilidade aumentada
deadzone = 0.01         # Menor zona morta para aceitar microajustes
smooth_factor = 0.85    # Suavização muito alta
last_x, last_y = None, None
smoothed_dx, smoothed_dy = 0.0, 0.0

def move_analog(delta_x, delta_y):
    global smoothed_dx, smoothed_dy

    # Suavização com média exponencial mais intensa
    smoothed_dx = (smooth_factor * smoothed_dx) + ((1 - smooth_factor) * delta_x)
    smoothed_dy = (smooth_factor * smoothed_dy) + ((1 - smooth_factor) * delta_y)

    # Aplica escala para controlar resposta
    x = max(min(smoothed_dx * scale, 1.0), -1.0)
    y = max(min(-smoothed_dy * scale, 1.0), -1.0)  # eixo Y invertido

    # Zona morta refinada
    if abs(x) < deadzone: x = 0.0
    if abs(y) < deadzone: y = 0.0

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

    # Ignora movimentos muito extremos
    if abs(delta_x) > 100 or abs(delta_y) > 100:
        return

    move_analog(delta_x, delta_y)

def start_listener():
    with Listener(on_move=on_move) as listener:
        listener.join()

# Roda em thread separada
threading.Thread(target=start_listener, daemon=True).start()
print("🎮 Controle suave ativado! Mouse agora com resposta fluida e precisa.")
input("Pressione Enter para encerrar...\n")
