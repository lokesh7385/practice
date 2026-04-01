import cv2
import numpy as np

class CursorSmoother:
    def __init__(self, process_noise=1e-5, measurement_noise=1e-1, error_cov=1.0):
        """
        Kalman Filter for 2D cursor tracking.
        State: [x, y, dx, dy]
        Measurement: [x, y]
        """
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0],
                                              [0, 1, 0, 0]], np.float32)
        
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0],
                                             [0, 1, 0, 1],
                                             [0, 0, 1, 0],
                                             [0, 0, 0, 1]], np.float32)
                                             
        self.kf.processNoiseCov = np.eye(4, dtype=np.float32) * process_noise
        self.kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * measurement_noise
        self.kf.errorCovPost = np.eye(4, dtype=np.float32) * error_cov
        
        self.first_frame = True

    def update(self, x, y):
        """
        x, y: Measured position (pixels or normalized, but consistent).
        Returns: Smoothed (x, y)
        """
        measurement = np.array([[np.float32(x)], [np.float32(y)]])
        
        if self.first_frame:
            # Initialize state with first measurement
            self.kf.statePost = np.array([[np.float32(x)], 
                                          [np.float32(y)], 
                                          [0], 
                                          [0]], np.float32)
            self.first_frame = False
            return x, y
        
        # Predict
        self.kf.predict()
        
        # Correct
        estimated = self.kf.correct(measurement)
        
        return float(estimated[0]), float(estimated[1])
