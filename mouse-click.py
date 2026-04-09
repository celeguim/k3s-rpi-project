import pyautogui
import time

while True:
    pyautogui.moveTo(500, 300)
    pyautogui.click(button="right")
    time.sleep(12)
    pyautogui.moveTo(1000, 300)
    pyautogui.click(button="right")
    time.sleep(12)
