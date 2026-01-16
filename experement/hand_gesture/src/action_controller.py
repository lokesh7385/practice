import pyautogui
import platform
import math

# OS-specific imports for Volume Control
if platform.system() == "Windows":
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class ActionController:
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()
        self.volume_interface = None
        self.min_vol = 0.0
        self.max_vol = 1.0
        
        if platform.system() == "Windows":
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume_interface = interface.QueryInterface(IAudioEndpointVolume)
                # Vol range usually -65.25 to 0.0 dB
                # But we will use scalar methods if possible or step up/down
            except Exception as e:
                print(f"Volume control init failed: {e}")

    def change_volume(self, increase=True):
        """Changes system volume by a step."""
        if self.volume_interface:
            # Step up/down 
            current_vol = self.volume_interface.GetMasterVolumeLevelScalar()
            step = 0.02 # 2% step
            new_vol = min(1.0, current_vol + step) if increase else max(0.0, current_vol - step)
            self.volume_interface.SetMasterVolumeLevelScalar(new_vol, None)
        else:
            # Fallback using pyautogui media keys
            key = 'volumeup' if increase else 'volumedown'
            pyautogui.press(key)

    def move_mouse(self, x_norm, y_norm, smooth_factor=0.5):
        """
        Moves mouse to (x_norm, y_norm) * screen_size.
        x_norm, y_norm are 0.0-1.0.
        """
        target_x = int(x_norm * self.screen_w)
        target_y = int(y_norm * self.screen_h)
        
        # Simple clamp
        target_x = max(0, min(self.screen_w, target_x))
        target_y = max(0, min(self.screen_h, target_y))

        # Direct move is jittery, usually smoothing is handled in state machine or main loop.
        # Here we just execute the move.
        pyautogui.moveTo(target_x, target_y)

    def left_click(self):
        pyautogui.click()

    def play_pause_media(self):
        pyautogui.press('playpause')

    def zoom(self, direction_in=True):
        """
        Zoom in or out.
        direction_in: True for Zoom In, False for Zoom Out.
        """
        # ctrl + +/- or scroll
        if direction_in:
            pyautogui.hotkey('ctrl', '+')
        else:
            pyautogui.hotkey('ctrl', '-')

    def close_tab(self):
        """Closes current browser tab."""
        pyautogui.hotkey('ctrl', 'w')
