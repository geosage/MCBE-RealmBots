import keyboard
import time
import pyautogui

time.sleep(5)
# Run the script indefinitely
while True:
    def hold_key(window_title, key, duration):
        # Simulate a key press
        keyboard.press(key)

        # Pause the script execution for the specified duration
        time.sleep(duration)

        # Simulate releasing the key
        keyboard.release(key)

    # Example usage: Hold down the 'A' key for 2 seconds in the window with title 'My Window'
    hold_key('Roblox', 'a', 1)

    hold_key('Roblox', 'd', 1)
    time.sleep(300)
    

