import time
import threading
from pynput import mouse
from vgamepad import VX360Gamepad
from math import copysign

gamepad = VX360Gamepad()

scaleX = 5000.0
scaleY = 400.0
smoothing = 9.0
noiseFilter = 14.0

deltaX = 0.0
deltaY = 0.0

def custom_curve(value):
    abs_val = abs(value)
    sign = copysign(1, value)

    if abs_val < 7000:
        return 0
    elif abs_val < 18000:
        return sign * 1337.0
    elif abs_val < 25000:
        return sign * 6000.0
    elif abs_val < 28888:
        return sign * 12337.0
    else:
        return sign * 19000.0

def apply_curve_and_scale(value, scale):
    curved = custom_curve(value)
    scaled = curved * scale / 10000.0
    return max(min(int(scaled), 32767), -32767)

def update_gamepad():
    global deltaX, deltaY
    while True:
        rightX = apply_curve_and_scale(deltaX, scaleX)
        rightY = apply_curve_and_scale(-deltaY, scaleY)

        gamepad.right_joystick(x_value=rightX, y_value=rightY)
        gamepad.update()

        deltaX *= (1.0 - (1.0 / smoothing))
        deltaY *= (1.0 - (1.0 / smoothing))

        time.sleep(0.005)

def on_move(x, y):
    global deltaX, deltaY
    if abs(x) > noiseFilter:
        deltaX += x
    if abs(y) > noiseFilter:
        deltaY += y

def listen_mouse():
    with mouse.Listener(on_move=lambda x, y: on_move(x, y)) as listener:
        listener.join()

# Executa as threads de leitura do mouse e atualização do controle
threading.Thread(target=update_gamepad, daemon=True).start()
listen_mouse()
