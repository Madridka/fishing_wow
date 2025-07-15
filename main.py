import cv2
import numpy as np
import pyautogui
import time

# Пути к шаблонам поплавка разных размеров
TEMPLATE_PATHS = [
    "bobber_large.png",
    "bobber_mid.png",
    "bobber_small.png"
]

# Координаты области поиска (x, y, w, h)
SEARCH_REGION = (0, 0, 800, 600)


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

        if max_val > best_val and max_val >= 0.45:
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
    timeout = 15

    while time.time() - start_time < timeout:
        time.sleep(0.1)
        curr_frame = pyautogui.screenshot(region=region)
        curr_gray = cv2.cvtColor(np.array(curr_frame), cv2.COLOR_RGB2GRAY)

        diff = cv2.absdiff(prev_gray, curr_gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        movement = np.sum(thresh)
        print(f"[DEBUG] movement: {movement}")

        if movement > 25000:
            return True

        prev_gray = curr_gray

    return False


def main():
    print("⏳ Запуск через 3 секунды...")
    time.sleep(3)

    while True:
        pyautogui.press('1')  # заброс
        time.sleep(1.5)

        pos = search_bobber()
        if pos:
            print(f"🎯 Поплавок найден: {pos}")
            pyautogui.moveTo(*pos)

            print("🕵️ Ждём клёва...")
            if detect_bite(pos):
                print("🐟 КЛЁВ! Кликаем!")
                time.sleep(0.5)
                pyautogui.rightClick()
            else:
                print("⌛ Клёва не было.")
        else:
            print("❌ Поплавок не найден.")

        time.sleep(2)


if __name__ == "__main__":
    main()
