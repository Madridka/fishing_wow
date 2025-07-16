import cv2
import numpy as np
import pyautogui
import time
import datetime

# Пути к шаблонам поплавка разных размеров
TEMPLATE_PATHS = [
    "1.png",
    "2.png",
    "3.png",
    "4.png",
    "5.png",
    "6.png",
    "7.png",
    "8.png",
]
movement_speed = 20000
value_to_click = 0.40
time_for_wait = 15
time_to_screen = 0.1
time_to_run_bot = 3
wait_time_after_run = 1.5
button_with_rod = '3'
sleep_before_click = 0.8
time_to_bait = 600
sleep_after_bait = 10

# Координаты области поиска (x, y, w, h)
SEARCH_REGION = (0, 0, 800, 600)
last_z_press = None


def check_and_press_z():
    global last_z_press
    now = datetime.datetime.now()
    if last_z_press is None or (now - last_z_press).total_seconds() >= time_to_bait:
        print("⌛ 15 минут прошло — нажимаем 2")
        pyautogui.press('2')
        time.sleep(sleep_after_bait)
        last_z_press = now


def load_templates():
    templates = []
    for path in TEMPLATE_PATHS:
        img = cv2.imread(path, 0)
        if img is not None:
            templates.append((img, path))
        else:
            print(f"[WARNING] Шаблон не загружен: {path}")
    return templates


def search_bobber():
    x, y, w, h = SEARCH_REGION
    screenshot = pyautogui.screenshot(region=SEARCH_REGION)
    screen_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    best_val = 0
    best_center = None

    templates = load_templates()

    for template, name in templates:
        res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print(f"[DEBUG] {name}: match quality = {max_val:.4f}")

        if max_val > best_val and max_val >= value_to_click:  # const
            top_left = max_loc
            center = (top_left[0] + template.shape[1] // 2,
                      top_left[1] + template.shape[0] // 2)
            best_val = max_val
            best_center = (x + center[0], y + center[1])

            # Отрисовка для дебага
            cv2.rectangle(screen_gray, top_left, (
                top_left[0] + template.shape[1], top_left[1] + template.shape[0]), 255, 2)

    cv2.imshow("Поиск поплавка", screen_gray)
    cv2.waitKey(1)

    return best_center


def detect_bite(center_pos):
    region_size = 100
    x = center_pos[0] - region_size // 2
    y = center_pos[1] - region_size // 2
    region = (x, y, region_size, region_size)

    prev_frame = pyautogui.screenshot(region=region)
    prev_gray = cv2.cvtColor(np.array(prev_frame), cv2.COLOR_RGB2GRAY)

    start_time = time.time()
    timeout = time_for_wait  # const

    zero_movement_count = 0

    while time.time() - start_time < timeout:
        time.sleep(time_to_screen)  # const
        curr_frame = pyautogui.screenshot(region=region)
        curr_gray = cv2.cvtColor(np.array(curr_frame), cv2.COLOR_RGB2GRAY)

        diff = cv2.absdiff(prev_gray, curr_gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        movement = np.sum(thresh)
        print(f"[DEBUG] movement: {movement}")

        if movement == 0:
            zero_movement_count += 1
            if zero_movement_count >= 5:
                print("[INFO] 5 подряд нулевых движений — выходим.")
                return False
        else:
            zero_movement_count = 0

        if movement > movement_speed:  # const
            print(f"[DEBUG] movement: {movement}")
            return True

        prev_gray = curr_gray

    return False


def main():
    print("⏳ Запуск через 3 секунды...")
    time.sleep(time_to_run_bot)  # const

    while True:
        check_and_press_z()
        pyautogui.press(button_with_rod)  # заброс #const
        time.sleep(wait_time_after_run)  # const

        pos = search_bobber()
        if pos:
            print(f"🎯 Поплавок найден: {pos}")
            pyautogui.moveTo(*pos)

            print("🕵️ Ждём клёва...")
            if detect_bite(pos):
                print("🐟 КЛЁВ! Кликаем!")
                time.sleep(sleep_before_click)  # const
                pyautogui.rightClick()
            else:
                print("⌛ Клёва не было.")
        else:
            print("❌ Поплавок не найден.")

        time.sleep(2)


if __name__ == "__main__":
    main()
