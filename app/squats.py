import time
import mediapipe as mp
import cv2
import numpy as np


# Define helper functions
def findAngle(a, b, c, minVis=0.8):
    if a.visibility > minVis and b.visibility > minVis and c.visibility > minVis:
        bc = np.array([c.x - b.x, c.y - b.y, c.z - b.z])
        ba = np.array([a.x - b.x, a.y - b.y, a.z - b.z])

        angle = np.arccos((np.dot(ba, bc)) / (np.linalg.norm(ba) * np.linalg.norm(bc))) * (180 / np.pi)

        return 360 - angle if angle > 180 else angle
    return -1


def legState(angle):
    if angle < 0:
        return 0
    elif angle < 105:
        return 1
    elif angle < 150:
        return 2
    return 3


repCount = 0
start_time = None
max_duration = 60


# Main squats function to be used in Flask route
def generate_squats_frames(source_type='webcam', video_path=None):
    global repCount, start_time
    start_time = time.time()
    repCount = 0
    lastState = 9
    stateMessages = []

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    if source_type == 'webcam':
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(video_path)

    # Reduce frame resolution for better performance
    cap.set(3, 640)  # Width
    cap.set(4, 480)  # Height

    frame_skip = 2  # Process every 2nd frame for performance boost
    frame_count = 0

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print('Camera error or frame not captured')
                break

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue  # Skip frames to reduce load

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False
            results = pose.process(frame_rgb)
            frame_rgb.flags.writeable = True
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            if not results.pose_landmarks:
                continue

            lm_arr = results.pose_landmarks.landmark
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            rAngle = findAngle(lm_arr[24], lm_arr[26], lm_arr[28])
            lAngle = findAngle(lm_arr[23], lm_arr[25], lm_arr[27])

            rState = legState(rAngle)
            lState = legState(lAngle)
            state = rState * lState

            stateMessages.clear()

            if state == 0:
                if rState == 0:
                    stateMessages.append("Right Leg Not Detected")
                if lState == 0:
                    stateMessages.append("Left Leg Not Detected")
            elif state % 2 == 0 or rState != lState:
                if lastState == 1:
                    if lState == 2 or lState == 1:
                        stateMessages.append("Fully extend left leg")
                    if rState == 2 or lState == 1:
                        stateMessages.append("Fully extend right leg")
                else:
                    if lState == 2 or lState == 3:
                        stateMessages.append("Fully retract left leg")
                    if rState == 2 or lState == 3:
                        stateMessages.append("Fully retract right leg")
            else:
                if state == 1 or state == 9:
                    if lastState != state:
                        lastState = state
                        if lastState == 1:
                            stateMessages.append("GOOD!")
                            repCount += 1

            # Display squat count
            cv2.putText(frame, f"Squats: {repCount}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                        cv2.LINE_AA)

            # Display state messages
            y_offset = 60
            for message in stateMessages:
                cv2.putText(frame, message, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
                y_offset += 30

                # Show the frame
                # Encode the frame for Flask streaming
                _, buffer = cv2.imencode('.jpg', frame)
                frame_1 = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_1 + b'\r\n')

            elapsed_time = time.time() - start_time
            if elapsed_time > max_duration:
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


def get_squats_count():
    return repCount

