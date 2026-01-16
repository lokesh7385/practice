import math
import numpy as np

def calculate_distance(p1, p2):
    """Calculates Euclidean distance between two points (x, y)."""
    x1, y1 = p1[1], p1[2]
    x2, y2 = p2[1], p2[2]
    return math.hypot(x2 - x1, y2 - y1)

def get_finger_states(lm_list):
    """
    Returns a list of 5 booleans [Thumb, Index, Middle, Ring, Pinky]
    indicating if the finger is extended (True) or closed (False).
    Based on landmark positions.
    """
    if not lm_list:
        return []

    fingers = []
    
    # Tips ids: 4, 8, 12, 16, 20
    # Pip ids: 2, 6, 10, 14, 18 (Knuckles/Lower joints for reference)
    
    # Thumb: Check if tip is to the right/left of knuckle depending on hand side
    # For simplicity in rule-based (assuming palm facing camera): 
    # Compare x-coord of tip (4) vs IP joint (3)
    # This logic changes based on Left/Right hand, simplified here to "outwards" check 
    # or just checking vertical for simple thumbs up/down
    
    # Better generic approach for Thumb:
    # Check simple distance from wrist vs index mcp? 
    # Let's simple check x-axis for now. 
    # NOTE: This is ambiguous without knowing handedness.
    # We will let Gesture Logic handle the nuances of Thumb with handedness context.
    # Here we just return coordinates or simple vertical checks for other fingers.
    
    # Fingers 2-5 (Index to Pinky)
    # Check if Tip y < Pip y (assuming Hand is upright)
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    
    # Thumbs logic usually handled specifically in recognizer, 
    # but here is a simple placeholder. 
    # We will skip thumb here and let recognizer handle it properly using handedness.
    
    for tip, pip in zip(tips, pips):
        if lm_list[tip][2] < lm_list[pip][2]: # Y-axis inverted in image space
            fingers.append(True)
        else:
            fingers.append(False)
            
    return fingers

def normalize_distance(dist, img_shape):
    """Normalize distance by diagonal size of image to handle depth changes somewhat."""
    h, w, c = img_shape
    diag = math.hypot(h, w)
    return dist / diag
