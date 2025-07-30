import pyautogui
import numpy as np
import cv2
import time
import threading
import vgamepad as vg
from ultralytics import YOLO

# Inicializa gamepad virtual
gamepad = vg.VX360Gamepad()

# Força e zona morta
assist_strength = 0.35
deadzone = 0.01

# Modelo YOLOv8 (use um modelo personalizado treinado para COD BO6)
model = YOLO("yolov8n.pt")  # Substitua pelo seu modelo customizado se houver

def detect_target():
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    results = model(img)[0]
    boxes = results.boxes

    if boxes:
        biggest = max(boxes, key=lambda b: b.xywh[0][2] * b.xywh[0][3])  # Maior área
        x_center = int(biggest.xywh[0][0])
        y_center = int(biggest.xywh[0][1])
        return x_center, y_center

    return None

def aim_loop():
    screen_w, screen_h = pyautogui.size()
    center_x, center_y = screen_w // 2, screen_h // 2

    while True:
        target = detect_target()

        if target:
            tx, ty = target
            dx = (tx - center_x) / screen_w
            dy = (ty - center_y) / screen_h

            dx *= assist_strength
            dy *= assist_strength

            if abs(dx) < deadzone: dx = 0.0
            if abs(dy) < deadzone: dy = 0.0

            gamepad.right_joystick_float(x_value_float=dx, y_value_float=dy)
            gamepad.update()
            print(f"🎯 Mira ajustada para ({dx:.2f}, {dy:.2f})")
        else:
            # Mantém analógico parado se não encontrar alvo
            gamepad.right_joystick_float(x_value_float=0.0, y_value_float=0.0)
            gamepad.update()

        time.sleep(0.05)

if __name__ == "__main__":
    print("🧠 Aim Assist com YOLOv8 iniciado (modo acadêmico)")
    threading.Thread(target=aim_loop, daemon=True).start()
    input("Pressione Enter para encerrar...\n")
