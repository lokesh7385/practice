import sys
try:
    import mediapipe as mp
    print(f"MediaPipe Version: {mp.__version__}")
    print(f"Dir(mp): {dir(mp)}")
    
    try:
        import mediapipe.python.solutions as solutions
        print("Success: import mediapipe.python.solutions worked!")
        print(f"Solutions: {solutions}")
        print(f"Dir(solutions): {dir(solutions)}")
    except ImportError as e:
        print(f"Failed to import mediapipe.python.solutions: {e}")

    try:
        print(f"mp.solutions: {mp.solutions}")
    except AttributeError:
        print("mp.solutions usage failed as expected.")

except Exception as e:
    print(f"General Error: {e}")
