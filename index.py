
import cv2
import mediapipe as mp
import pyautogui
import math
import time
import webbrowser


# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

# Get screen size
screen_w, screen_h = pyautogui.size()

# Track previous finger positions
prev_x, prev_y = 0, 0
swipe_threshold = 100  # Pixels to register a swipe
jump_threshold = 0.1  # Distance for jump action
roll_threshold = 0.08  # Distance for roll action
hand_move_threshold = 50  # Pixels to detect hand movement

# # Function to open Chrome
# def open_chrome():
#     webbrowser.open("https://www.google.com")

with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Mirror the frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get index finger tip position
                index_finger_tip = hand_landmarks.landmark[8]
                x = int(index_finger_tip.x * screen_w)
                y = int(index_finger_tip.y * screen_h)
                pyautogui.moveTo(x, y)  # Move the mouse

                # Detect thumb and index finger pinch for click
                thumb_tip = hand_landmarks.landmark[4]
                distance = math.hypot(thumb_tip.x - index_finger_tip.x, thumb_tip.y - index_finger_tip.y)

                if distance < 0.05:  # Click when fingers are close
                    pyautogui.click()

                # Scroll with hand position
                if index_finger_tip.y < 0.3:
                    pyautogui.scroll(10)  # Scroll up
                elif index_finger_tip.y > 0.7:
                    pyautogui.scroll(-10)  # Scroll down

                # Detect jump (fist up - all fingers curled)
                fingers_curled = all(hand_landmarks.landmark[i].y > hand_landmarks.landmark[i - 2].y for i in [8, 12, 16, 20])
                if fingers_curled and hand_landmarks.landmark[0].y < 0.4:
                    pyautogui.press("space")

                # Detect swipe left/right using fist rotation
                wrist_x = hand_landmarks.landmark[0].x
                pinky_x = hand_landmarks.landmark[20].x
                if fingers_curled:
                    if pinky_x - wrist_x > 0.1:  # Fist rotated right
                        pyautogui.press("right")  # Swipe right
                    elif wrist_x - pinky_x > 0.1:  # Fist rotated left
                        pyautogui.press("left")  # Swipe left

                # Detect roll gesture (fist down - refresh page)
                if fingers_curled and hand_landmarks.landmark[0].y > 0.7:
                    pyautogui.hotkey("ctrl", "r")

                # Detect opening Chrome
                pinky_tip = hand_landmarks.landmark[20]
                if abs(pinky_tip.y - index_finger_tip.y) < 0.05 and abs(pinky_tip.x - index_finger_tip.x) < 0.05:
                    # open_chrome()
                    time.sleep(1)  # Prevent multiple triggers

                # Detect overall hand movement for navigation
                hand_x = int(hand_landmarks.landmark[0].x * screen_w)
                hand_y = int(hand_landmarks.landmark[0].y * screen_h)
                if prev_x != 0 and prev_y != 0:
                    if hand_x - prev_x > hand_move_threshold:
                        pyautogui.press("right")  # Move right
                    elif prev_x - hand_x > hand_move_threshold:
                        pyautogui.press("left")  # Move left
                    if hand_y - prev_y > hand_move_threshold:
                        pyautogui.press("down")  # Move down
                    elif prev_y - hand_y > hand_move_threshold:
                        pyautogui.press("up")  # Move up
                prev_x, prev_y = hand_x, hand_y

        cv2.imshow("Hand Gesture Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
