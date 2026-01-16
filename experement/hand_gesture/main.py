import cv2
import time
from src.hand_detector import HandDetector
from src.gesture_recognizer import GestureRecognizer
from src.action_controller import ActionController
from src.state_machine import StateMachine

def main():
    # 1. Init
    cap = cv2.VideoCapture(0)
    cap.set(3, 640) # Width
    cap.set(4, 480) # Height
    
    detector = HandDetector(max_hands=2, detection_con=0.7)
    recognizer = GestureRecognizer()
    controller = ActionController()
    state_machine = StateMachine()
    
    print("Hand Gesture Control Started. Press 'q' to exit.")

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read webcam.")
            break
            
        # Flip image for mirror effect (natural interaction)
        img = cv2.flip(img, 1)
        
        # 2. Detect Hands
        img = detector.find_hands(img)
        lm_list_all = []
        
        # We need to associate landmarks with 'Left' or 'Right' hand accurately
        # MediaPipe's multi_handedness gives us labels.
        # Note: If we flipped the image, the label 'Left' usually means the user's Left hand 
        # (which appears on the Left side of the screen now). 
        # But let's rely on the detector's output mapping.
        
        # HandDetector.find_hands processes the image. 
        # We can extract data now.
        
        landmarks_map = {} # 'Left' -> lm_list, 'Right' -> lm_list
        
        if detector.results.multi_hand_landmarks:
            for idx, hand_handedness in enumerate(detector.results.multi_handedness):
                label = hand_handedness.classification[0].label
                # If we flipped the image, MP still thinks in original coordinates usually?
                # Actually, if we pass the flipped image to MP, 'Left' label means 
                # "This looks like a Left Hand". 
                # If you hold up your left hand to a mirror, it looks like a right hand.
                # MP is trained on selfie mode usually? 
                # Let's just trust the label for now and debug if swapped.
                
                lm_list = []
                my_hand = detector.results.multi_hand_landmarks[idx]
                h, w, c = img.shape
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
            if gesture_name == "Hands Distance":
                 extra_data = gesture_name[1] # It returned a tuple ("Hands Distance", dist)
                 gesture_name = "Hands Distance" # Reset name string
                 # Wait, my logic in recognizer returned tuple.
                 # Let's fix line above:
                 # In recognizer: return ("Hands Distance", wrist_dist)
                 # So gesture_name is the Tuple.
                 pass # logic handled below by checking type or unpacking

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
                
                if gesture_name == "Two Fingers":
                    # Extract cursor coordinates (Index Tip)
                    index_x = lm_list[8][1]
                    index_y = lm_list[8][2]
                    # Normalize
                    h, w, _ = img.shape
                    norm_x = index_x / w
                    norm_y = index_y / h
                    extra_data = (norm_x, norm_y)

        # 4. State Machine & Action
        if gesture_name:
            current_gesture_text = gesture_name
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

        cv2.imshow("Hand Gesture Control (Press 'q' to exit)", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
