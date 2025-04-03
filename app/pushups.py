import cv2
import mediapipe as mp
import numpy as np
from flask import Response
import time

# Initialize Mediapipe pose model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Function to calculate the angle between three points
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

# Push-Up Counting Variables
counter = 0
down_position = False
start_time = None
max_duration = 60  # 60 seconds test

MIN_HIP_ANGLE = 150  # Minimum hip angle for a straight body
MIN_ELBOW_ANGLE = 90  # Minimum elbow angle in the downward phase
MAX_ELBOW_ANGLE = 160  # Maximum elbow angle in the upward phase

def generate_frames():
    global counter, down_position, start_time

    cap = cv2.VideoCapture(0)  # Open webcam
    start_time = time.time()  # Start the test timer
    counter = 0  # Reset push-up counter

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip and process the frame
        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            # Extract landmarks
            landmarks = results.pose_landmarks.landmark

            # Get coordinates for relevant points
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y
            left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y

            # Calculate angles
            hip_angle = calculate_angle(shoulder, hip, knee)
            elbow_angle = calculate_angle(shoulder, elbow, wrist)

            # Get shoulder and wrist heights
            shoulder_height = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
            wrist_height = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y

            # Initial shoulder height for thresholding

            # Check if wrist is close to the ground
            GROUND_THRESHOLD = 1  # Adjust based on camera angle and resolution

            # Check if wrists are near the ground
            if (
                    abs(left_wrist - left_ankle) < GROUND_THRESHOLD
            ):
                wrists_on_ground = True
            else:
                wrists_on_ground = False

            # Check if in push-up position (hip angle and wrist ground proximity)
            if hip_angle > MIN_HIP_ANGLE and wrists_on_ground:
                # Downward motion detected
                if elbow_angle < MIN_ELBOW_ANGLE:
                    down_position = True

                # Upward motion detected
                if down_position and elbow_angle > MAX_ELBOW_ANGLE:
                    counter += 1
                    down_position = False

            # Display landmarks
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Display angles and counter
            cv2.putText(image, f'Hip Angle: {int(hip_angle)}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(image, f'Elbow Angle: {int(elbow_angle)}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),
                        2)
            cv2.putText(image, f'Push-ups: {counter}', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(image, f'Time: {time.time() - start_time}', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                        2)

        # Show the frame
        # Encode the frame for Flask streaming
        _, buffer = cv2.imencode('.jpg', image)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        elapsed_time = time.time() - start_time
        if elapsed_time > max_duration:
            break
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()


# Function to get final push-up count
def get_pushup_count():
    return counter
