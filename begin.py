import cv2  
import mediapipe as mp  
import pyautogui 
import math 
import time  
# import webbrowser


mp_hands = mp.solutions.hands   
mp_drawing = mp.solutions.drawing_utils 
cap = cv2.VideoCapture(0) 


screen_w, screen_h = pyautogui.size() 


keyboard_keys = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'SPACE']
]


key_width = screen_w // 10
key_height = 50
keyboard_y = screen_h - 200  

def get_key(x, y):
    """ Returns the key at the given x, y position. """
    row_index = (y - keyboard_y) // key_height
    col_index = x 

    if 0 <= row_index < len(keyboard_keys) and 0 <= col_index < len(keyboard_keys[row_index]):
        return keyboard_keys[row_index][col_index]
    return None

with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                
                index_finger_tip = hand_landmarks.landmark[8]
                x = int(index_finger_tip.x * screen_w)
                y = int(index_finger_tip.y * screen_h)
                pyautogui.moveTo(x, y) 

                
                thumb_tip = hand_landmarks.landmark[4]
                distance = math.hypot(thumb_tip.x - index_finger_tip.x, thumb_tip.y - index_finger_tip.y)

                if distance < 0.05:  
                    key = get_key(x, y)
                    if key:
                        if key == "SPACE":
                            pyautogui.write(" ")
                        else:
                            pyautogui.write(key.lower())
                        time.sleep(0.3)  

              
                if index_finger_tip.y < 0.3:
                    pyautogui.scroll(10)  
                elif index_finger_tip.y > 0.7:
                    pyautogui.scroll(-10)  

        
        for i, row in enumerate(keyboard_keys):
            for j, key in enumerate(row):
                x1 = j * key_width
                y1 = keyboard_y + (i * key_height)
                x2 = x1 + key_width
                y2 = y1 + key_height
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                cv2.putText(frame, key, (x1 + 10, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Hand Gesture Control with Virtual Keyboard", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
