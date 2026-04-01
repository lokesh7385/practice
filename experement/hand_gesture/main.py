import cv2
import time
import pyautogui
from src.hand_detector import HandDetector
from src.gesture_recognizer import GestureRecognizer
from src.action_controller import ActionController
from src.state_machine import StateMachine
from src.smoother import CursorSmoother

def main():
    # 1. Init
    cap = cv2.VideoCapture(0)
    
    # Increase FPS if possible
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(3, 640) # Width
    cap.set(4, 480) # Height
    
    detector = HandDetector(max_hands=2, detection_con=0.7)
    recognizer = GestureRecognizer()
    controller = ActionController()
    state_machine = StateMachine()
    
    # Kalman Smoother: adjust noise params if needed (process_noise, measurement_noise)
    smoother = CursorSmoother(process_noise=0.01, measurement_noise=10, error_cov=1.0)
    
    # Relative Tracking State
    screen_w, screen_h = pyautogui.size()
    curr_cursor_x, curr_cursor_y = pyautogui.position()
    
    prev_hand_x = None
    prev_hand_y = None
    
    SENSITIVITY = 2.0
    
    print("Hand Gesture Control Started. Press 'q' to exit.")

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read webcam.")
            break
            
        # Flip image for mirror effect
        img = cv2.flip(img, 1)
        h, w, c = img.shape
        
        # 2. Detect Hands
        img = detector.find_hands(img)
        
        landmarks_map = {} # 'Left' -> lm_list, 'Right' -> lm_list
        
        if detector.results.multi_hand_landmarks:
            for idx, hand_handedness in enumerate(detector.results.multi_handedness):
                label = hand_handedness.classification[0].label
                lm_list = []
                my_hand = detector.results.multi_hand_landmarks[idx]
                
                for id, lm in enumerate(my_hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])
                landmarks_map[label] = lm_list

        current_gesture_text = "None"
        triggered_action_text = ""

        # 3. Recognize & Act
        # Prioritize 2-hand gestures first
        gesture_name = recognizer.check_two_hand_gestures(landmarks_map)
        extra_data = None
        
        if gesture_name:
            if isinstance(gesture_name, tuple):
                 extra_data = gesture_name[1]
                 gesture_name = gesture_name[0]
        else:
            # Check single hand gestures
            # Prefer Right hand for cursor/main control if available, else Left
            active_hand_label = "Right" if "Right" in landmarks_map else ("Left" if "Left" in landmarks_map else None)
            
            if active_hand_label:
                lm_list = landmarks_map[active_hand_label]
                gesture_name = recognizer.recognize(lm_list, active_hand_label, landmarks_map)
                
                # --- Relative Tracking Logic ---
                # Track using Palm Center (Middle Finger MCP - id 9) or Wrist(0)
                # Middle MCP (9) is more stable than tip.
                raw_x = lm_list[9][1]
                raw_y = lm_list[9][2]
                
                # 1. Smooth the raw input
                smooth_x, smooth_y = smoother.update(raw_x, raw_y)
                
                # 2. Calculate Delta
                if prev_hand_x is not None:
                     dx = smooth_x - prev_hand_x
                     dy = smooth_y - prev_hand_y
                     
                     # 3. Apply Sensitivity
                     # Note: if camera is mirrored/flipped, dx likely matches screen direction?
                     # Flipped horiz: Moving hand Right in reality -> Right on screen (if flipped) -> Pixels increase
                     # Coordinate system: x increases right, y increases down.
                     # Screen: x increases right, y increases down.
                     # Matches.
                     
                     # Only move if gesture allows (Open Palm or Two Fingers)
                     # Or always move if hand present? User requested "touchpad style".
                     # Typically touchpad works when contact is made. Here "contact" = Hand Visible.
                     # But we might want to pause tracking if making other gestures?
                     # Let's say: "Fist" -> Pause/Static (so it triggers action but doesn't drag).
                     # "Open Palm", "Two Fingers", "Pinch" -> Move.
                     
                     if gesture_name in ["Open Palm", "Two Fingers", "Pinch"]:
                         curr_cursor_x += dx * SENSITIVITY
                         curr_cursor_y += dy * SENSITIVITY
                         
                         # 4. Clamp
                         curr_cursor_x = max(0, min(screen_w - 1, curr_cursor_x))
                         curr_cursor_y = max(0, min(screen_h - 1, curr_cursor_y))
                         
                         # Pass these absolute coords to move_mouse via action or directly?
                         extra_data = (curr_cursor_x / screen_w, curr_cursor_y / screen_h)
                
                # Update prev
                prev_hand_x = smooth_x
                prev_hand_y = smooth_y
            else:
                 # Hand lost: Do NOT reset prev_hand_x/y to None immediately if we want "continue where left off" 
                 # BUT when hand re-appears, if we compare to OLD prev, we get a huge jump (Deltas).
                 # So when hand is LOST, we should probably reset prev to avoid jump on re-entry.
                 # "If no hand is detected, do NOT move cursor and do NOT reset previous values" -> This implies preserving cursor pos.
                 # But it explicitly says "Update prev_x, prev_y every frame" which implies tracking continuity?
                 # No, if hand exits frame, we have no x/y.
                 # When hand re-enters at a NEW position, dx = new_pos - old_pos (huge jump).
                 # This contradicts "touchpad style" which usually means: 
                 # Lift finger (exit frame) -> Place finger elsewhere (re-enter) -> No cursor jump (dx should be 0 for that first frame).
                 
                 # So: If hand was NOT present last frame but IS present this frame -> Reset prev (dx=0).
                 prev_hand_x = None
                 prev_hand_y = None

        # 4. State Machine & Action
        if gesture_name:
            current_gesture_text = gesture_name
            # If we calculated cursor position, pass it.
            # State machine might smooth it again? 
            # We applied Kalman. State machine has deque smoothing for "Two Fingers" legacy support.
            # We should bypass state machine smoothing if we handled it here?
            # Or just pass the final coords.
            
            action, data = state_machine.get_action(gesture_name, extra_data)
            
            if action:
                triggered_action_text = f"Action: {action}"
                print(f"Triggered: {action}")
                
                if action == "PLAY_PAUSE":
                    controller.play_pause_media()
                elif action == "VOL_UP":
                    controller.change_volume(increase=True)
                elif action == "VOL_DOWN":
                    controller.change_volume(increase=False)
                elif action == "CLICK":
                    controller.left_click()
                elif action == "MOVE_MOUSE":
                    if data:
                        # Data is normalized (0-1)
                        # We used our calculated absolute coords -> converted to norm -> passed to State Machine -> passed back
                        controller.move_mouse(data[0], data[1])
                elif action == "ZOOM":
                    controller.zoom(direction_in=(data == "IN"))
                elif action == "CLOSE_TAB":
                    controller.close_tab()

        # 5. UI / Render
        cv2.putText(img, f"Gesture: {current_gesture_text}", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if triggered_action_text:
             cv2.putText(img, triggered_action_text, (10, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Draw Tracking Point
        if active_hand_label and gesture_name in ["Open Palm", "Two Fingers", "Pinch"]:
             # Visualize cursor on screen (circles on camera feed? maybe just tracking dot)
             # Draw the SMOOTHED hand point
             if prev_hand_x is not None:
                cv2.circle(img, (int(prev_hand_x), int(prev_hand_y)), 10, (255, 0, 255), cv2.FILLED)

        cv2.imshow("Hand Gesture Control (Press 'q' to exit)", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
