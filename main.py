import cv2
import numpy as np
import pyautogui
import time

# Загружаем шаблон
template = cv2.imread("bobber.png", 0)
w, h = template.shape[::-1]

# Координаты области поиска
SEARCH_REGION = (0, 0, 800, 600)  # x, y, w, h

def search_bobber():
    x, y, w, h = SEARCH_REGION
    screenshot = pyautogui.screenshot(region=SEARCH_REGION)
    screen_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    print(f"[DEBUG] match quality: {max_val:.4f}")  # отладка

    if max_val >= 0.5:
        top_left = max_loc
        bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])
        cv2.rectangle(screen_gray, top_left, bottom_right, 255, 2)
        cv2.imshow("Found", screen_gray)
        cv2.waitKey(1)  # не 0! иначе зависнет

        center = (top_left[0] + template.shape[1] // 2, top_left[1] + template.shape[0] // 2)
        return (x + center[0], y + center[1])
    else:
        cv2.imshow("Not found", screen_gray)
        cv2.waitKey(1)
    return None

def detect_bite(center_pos):
    region_size = 100
    x = center_pos[0] - region_size // 2
    y = center_pos[1] - region_size // 2
    region = (x, y, region_size, region_size)

    prev_frame = pyautogui.screenshot(region=region)
    prev_gray = cv2.cvtColor(np.array(prev_frame), cv2.COLOR_RGB2GRAY)

    start_time = time.time()
    timeout = 15  # максимум 8 секунд на клёв

    while time.time() - start_time < timeout:
        time.sleep(0.1)
        curr_frame = pyautogui.screenshot(region=region)
        curr_gray = cv2.cvtColor(np.array(curr_frame), cv2.COLOR_RGB2GRAY)

        diff = cv2.absdiff(prev_gray, curr_gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        movement = np.sum(thresh)
        print(f"[DEBUG] movement: {movement}")

        if movement > 25000:  # число можно подогнать
            return True

        prev_gray = curr_gray

    return False


def main():
    print("⏳ Запуск через 3 секунды...")
    time.sleep(2)

    while True:
        pyautogui.press('1')  # заброс
        time.sleep(1)

        pos = search_bobber()
        if pos:
            print(f"🎯 Поплавок найден: {pos}")
            pyautogui.moveTo(*pos)

            print("🕵️ Ждём клёва...")
            if detect_bite(pos):
                print("🐟 КЛЁВ! Кликаем!")
                time.sleep(1)
                pyautogui.rightClick()
            else:
                print("⌛ Клёва не было.")
        else:
            print("❌ Поплавок не найден.")

        time.sleep(3)

if __name__ == "__main__":
    main()