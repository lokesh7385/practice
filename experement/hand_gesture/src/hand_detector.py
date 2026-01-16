import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, max_hands=2, detection_con=0.7, track_con=0.5):
        self.max_hands = max_hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.max_hands,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_positions(self, img, hand_no=0):
        lm_list = []
        if self.results.multi_hand_landmarks:
            if hand_no < len(self.results.multi_hand_landmarks):
                my_hand = self.results.multi_hand_landmarks[hand_no]
                for id, lm in enumerate(my_hand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])
        return lm_list

    def get_world_landmarks(self, hand_no=0):
        """Returns the world coordinates (meters) which are better for angles/relative distances independent of screen."""
        if self.results.multi_hand_world_landmarks:
             if hand_no < len(self.results.multi_hand_world_landmarks):
                return self.results.multi_hand_world_landmarks[hand_no]
        return None

    def get_handedness(self):
        """Returns 'Left' or 'Right' for each detected hand."""
        output = []
        if self.results.multi_handedness:
            for hand_metadata in self.results.multi_handedness:
                # MediaPipe assumes mirrored image by default, so Label 'Left' usually appears on the right of screen
                # but for self-view we want to flip it or just trust the label if we flipped the image beforehand.
                # The caller (main.py) will likely flip the image horizontally.
                output.append(hand_metadata.classification[0].label)
        return output
