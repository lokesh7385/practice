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
        # fingers: [Thumb, Index, Middle, Ring, Pinky] (Booleans) but thumb is tricky in generic util.
        # Let's refine thumb logic here based on hand_label.
        
        # Refine Thumb State
        # Thumb tip: 4, IP: 3, MCP: 2. 
        # Right Hand: Thumb is to the Left of Index (if palm facing user). 
        # Actually standard MediaPipe "Right" hand means it's your Right hand.
        # If showing palm to camera: Thumb x < Index x? No, Thumb is on the left side of image (if mirrored).
        # Let's assume standard selfie view (mirrored):
        # Right Hand (appears on right side of screen if NOT flipped, left if flipped).
        # We will assume "img" passed to detector was flipped via cv2.flip(1).
        # So Right Hand appears on Right Side of generic logic? No usually it mirrors your movement.
        # Let's stick to coordinate geometry relative to the hand itself.
        
        thumb_tip = lm_list[4]
        thumb_ip = lm_list[3]
        pinky_tip = lm_list[20]
        wrist = lm_list[0]
        
        # Robust Thumb Open check: Distance from tip to pinky MCP(17) vs IP to pinky MCP?
        # Or simply: Is thumb tip far from palm center?
        
        # Simple x-axis check.
        # If Right Hand: Open Thumb means Tip.x < IP.x (moving left/outwards if palm faces cam)
        # Wait, if palm faces cam, Right Hand thumb is on the Left side of the hand geometry.
        is_thumb_open = False
        if hand_label == "Right":
            if thumb_tip[1] < thumb_ip[1]: # Moving Left (which is Outwards for Right hand palm-facing)
                is_thumb_open = True
        else: # Left Hand
            if thumb_tip[1] > thumb_ip[1]: # Moving Right (Outwards)
                is_thumb_open = True
        
        # Override the generic utils thumb result
        fingers_extended = [is_thumb_open] + fingers 
        # fingers from utils calculates [Index...Pinky] actually? 
        # utils.get_finger_states logic:
        # tips = [8, 12, 16, 20], pips = [6, 10, 14, 18]
        # It returned 4 items? Let's check utils.
        # Ah, looking at utils, I should verify what it returns. 
        # It loops zip(tips, pips) which is 4 items.
        # So fingers in recognize is [Index, Middle, Ring, Pinky] (4 items).
        
        full_fingers = [is_thumb_open] + fingers # Now it's 5 items.
        
        # 1. Open Palm (All 5 Up)
        if all(full_fingers):
            return "Open Palm"

        # 2. Thumbs Up / Down
        # Criteria: Thumb Open, Others Closed.
        if is_thumb_open and not any(fingers): # fingers are the 4 non-thumb
            # Check orientation. User says "Thumb extended upward/downward".
            # Compare Thumb Tip Y vs Thumb IP Y
            if thumb_tip[2] < thumb_ip[2]: # Tip above IP (smaller Y)
                return "Thumbs Up"
            else:
                return "Thumbs Down"

        # 3. Two Fingers (Index + Middle Open, Others Closed) -> Cursor
        if full_fingers[1] and full_fingers[2] and not full_fingers[3] and not full_fingers[4] and not is_thumb_open:
             return "Two Fingers"
             
        # Alternate Two Fingers (thumb might be loose):
        # Strict: Index & Middle UP. Ring & Pinky DOWN. Thumb ignored? 
        # Prompt says "Index + middle finger extended". Usually implies strict.
        
        # 4. Pinch (Index and Thumb close)
        # Usually requires Index Up? Or just tips close?
        # Prereq: Index and Thumb are the active ones.
        dist_pinch = calculate_distance(lm_list[4], lm_list[8])
        # We need a dynamic threshold. 
        # Use distance between Wrist (0) and Index MCP (5) as scale reference.
        scale_ref = calculate_distance(lm_list[0], lm_list[5])
        if dist_pinch < scale_ref * 0.3: # Threshold 0.3 of palm size
             if full_fingers[1]: # Index is technically "up" or active loop
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
             # Also check orientation? Vertical hands?
             # For now, proximity is good enough for v1.
             return "Namaste"

        # 6. Distance Change (Zoom)
        # This is state-dependent (delta), but here we just return the Current Distance
        # The main loop/state machine will compare with previous frame.
        # We return a special gesture type with data.
        return ("Hands Distance", wrist_dist) 
