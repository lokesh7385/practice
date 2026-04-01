from .gesture_utils import calculate_distance, get_finger_states
import math

class GestureRecognizer:
    def __init__(self):
        pass

    def recognize(self, lm_list, hand_label, handedness_dict):
        """
        Recognizes gesture for a single hand or combined state.
        handedness_dict: Stores 'Left'/'Right' -> lm_list for 2-hand gestures.
        
        Returns: gesture_name (str) or None
        """
        if not lm_list:
            return None

        fingers = get_finger_states(lm_list)
        # fingers: [Thumb, Index, Middle, Ring, Pinky] (Booleans) from utils is actually only 4 fingers?
        # Let's check utils again or just implement robust logic here.
        # To be safe, let's recalculate fingers here or rely on utils if we trust it.
        # Previous analysis showed utils returned 4 items [Index...Pinky].
        # We need 5 items.
        
        # Correction: The previous `recognize` method manually added thumb.
        # Let's do a robust check again.
        
        thumb_tip = lm_list[4]
        thumb_ip = lm_list[3]
        
        # Robust Thumb Check
        is_thumb_open = False
        if hand_label == "Right":
            # Right Hand Palm Facing Camera: Thumb is on Left. Open means Tip < IP (Leftwards)
            if thumb_tip[1] < thumb_ip[1]: 
                is_thumb_open = True
        else:
            # Left Hand Palm Facing Camera: Thumb is on Right. Open means Tip > IP (Rightwards)
            if thumb_tip[1] > thumb_ip[1]:
                is_thumb_open = True
                
        # Utils gives us [Index, Middle, Ring, Pinky]
        four_fingers = fingers 
        full_fingers = [is_thumb_open] + four_fingers
        
        # 1. Open Palm (All 5 Up)
        if all(full_fingers):
            return "Open Palm"

        # 2. Fist (All Closed)
        if not any(full_fingers):
            return "Fist"

        # 3. Thumbs Up / Down
        # Criteria: Thumb Open, Others Closed.
        if is_thumb_open and not any(four_fingers): 
            if thumb_tip[2] < thumb_ip[2]: # Tip above IP
                return "Thumbs Up"
            else:
                return "Thumbs Down"

        # 4. Two Fingers (Index + Middle Open, Others Closed) -> Cursor / Scroll?
        # Typically "Peace Sign"
        if full_fingers[1] and full_fingers[2] and not full_fingers[3] and not full_fingers[4]:
             return "Two Fingers"
             
        # 5. Pinch (Index and Thumb close, Index usually Extended or Curved)
        # Check distance between Index Tip (8) and Thumb Tip (4)
        dist_pinch = calculate_distance(lm_list[4], lm_list[8])
        scale_ref = calculate_distance(lm_list[0], lm_list[5]) # Wrist to Index MCP
        
        if dist_pinch < scale_ref * 0.25: # Very close threshold
             # Also ensure other fingers are not all open (avoid confusion with Open Palm if thumb/index momentarily close)
             # But pinch is usually just those two.
             # Let's say if Ring and Pinky are closed, it's definitely a pinch used for clicking.
             if not full_fingers[3] and not full_fingers[4]:
                 return "Pinch"

        return "Unknown"

    def check_two_hand_gestures(self, landmarks_map):
        """
        landmarks_map: {'Right': lm_list, 'Left': lm_list}
        """
        if 'Right' not in landmarks_map or 'Left' not in landmarks_map:
            return None

        left_lm = landmarks_map['Left']
        right_lm = landmarks_map['Right']

        # 7. Namaste (Palms Together)
        # Check distance between Wrists and Middle Finger Tips
        wrist_dist = calculate_distance(left_lm[0], right_lm[0])
        middle_dist = calculate_distance(left_lm[12], right_lm[12])
        
        # Scale ref (average palm size)
        scale = (calculate_distance(left_lm[0], left_lm[5]) + calculate_distance(right_lm[0], right_lm[5])) / 2
        
        if wrist_dist < scale * 1.5 and middle_dist < scale * 1.5:
             return "Namaste"

        # 6. Distance Change (Zoom)
        # Return distance for zooming logic
        return ("Hands Distance", wrist_dist)
