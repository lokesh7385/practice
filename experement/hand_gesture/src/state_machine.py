import time
from collections import deque
import statistics

class StateMachine:
    def __init__(self):
        self.last_action_time = {} # Map action -> timestamp
        self.cooldown_default = 1.0 # Standard cooldown in seconds
        self.cooldown_continuous = 0.1 # Faster cooldown for volume/zoom/cursor
        
        # Namaste Logic
        self.namaste_start_time = None
        self.NAMASTE_HOLD_DURATION = 1.0
        
        # Cursor Smoothing
        self.cursor_history_x = deque(maxlen=5)
        self.cursor_history_y = deque(maxlen=5)
        
        # Zoom Logic
        self.last_zoom_dist = None
        
        # Current State
        self.current_gesture = None
        
    def get_action(self, gesture, extra_data=None):
        """
        Determines if an action should be triggered based on gesture and state (cooldowns).
        Returns: (ActionName, ActionData) or (None, None)
        """
        now = time.time()
        
        # Reset Namaste timer if gesture checks fails
        if gesture != "Namaste":
            self.namaste_start_time = None
        
        if gesture == "Hands Distance":
            # Zoom Logic (Continuous but needs delta)
            curr_dist = extra_data
            if self.last_zoom_dist is None:
                self.last_zoom_dist = curr_dist
                return None, None
            
            delta = curr_dist - self.last_zoom_dist
            self.last_zoom_dist = curr_dist
            
            # Threshold for zoom change
            if abs(delta) > 0.02: # small threshold
                # If negative -> Closer -> Zoom Out
                # If positive -> Further -> Zoom In
                return "ZOOM", "IN" if delta > 0 else "OUT"
            return None, None
            
        else:
            self.last_zoom_dist = None # Reset zoom tracking if gesture changes
            
        if gesture == "Open Palm":
            if self._check_cooldown("PLAY_PAUSE", self.cooldown_default, now):
                return "PLAY_PAUSE", None
        
        elif gesture == "Thumbs Up":
            if self._check_cooldown("VOL_UP", 0.2, now): # Faster than default, slower than continuous
                return "VOL_UP", None
                
        elif gesture == "Thumbs Down":
            if self._check_cooldown("VOL_DOWN", 0.2, now):
                return "VOL_DOWN", None
                
        elif gesture == "Pinch":
             if self._check_cooldown("CLICK", 0.5, now):
                 return "CLICK", None
                 
        elif gesture == "Two Fingers":
            # Cursor is continuous, no real cooldown, just smoothing
            # extra_data should be (x, y) normalized
            if extra_data:
                smooth_x, smooth_y = self._smooth_cursor(extra_data[0], extra_data[1])
                return "MOVE_MOUSE", (smooth_x, smooth_y)
                
        elif gesture == "Namaste":
            if self.namaste_start_time is None:
                self.namaste_start_time = now
            
            elapsed = now - self.namaste_start_time
            if elapsed >= self.NAMASTE_HOLD_DURATION:
                if self._check_cooldown("CLOSE_TAB", 3.0, now): # Long cooldown for safety
                    self.namaste_start_time = None # Reset
                    return "CLOSE_TAB", None
            else:
                 # Optional: Return progress for UI?
                 pass
                 
        return None, None

    def _check_cooldown(self, action_name, duration, now):
        last = self.last_action_time.get(action_name, 0)
        if now - last > duration:
            self.last_action_time[action_name] = now
            return True
        return False
        
    def _smooth_cursor(self, x, y):
        self.cursor_history_x.append(x)
        self.cursor_history_y.append(y)
        
        if len(self.cursor_history_x) < 2:
            return x, y
            
        return statistics.mean(self.cursor_history_x), statistics.mean(self.cursor_history_y)
