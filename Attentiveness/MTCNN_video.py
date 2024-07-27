import math
import cv2
from mtcnn.mtcnn import MTCNN
import matplotlib.pyplot as plt
import json
from flask import Flask, jsonify, render_template_string

# Initialize the detector
detector = MTCNN()

# Flask API Setup
app = Flask(__name__)

def process_frame(frame, confidence_threshold=0.9):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB for displaying with matplotlib

    # Detect faces in the image
    location = detector.detect_faces(img_rgb)

    def calculate_angles(landmarks):
        # Unpack landmarks
        left_eye = landmarks['left_eye']
        right_eye = landmarks['right_eye']
        nose = landmarks['nose']
        left_mouth = landmarks['mouth_left']
        right_mouth = landmarks['mouth_right']

        # Calculate roll angle
        dY = right_eye[1] - left_eye[1]
        dX = right_eye[0] - left_eye[0]
        roll = math.degrees(math.atan2(dY, dX))

        # Calculate yaw angle
        eye_center = ((left_eye[0] + right_eye[0]) * 0.5, (left_eye[1] + right_eye[1]) * 0.5)
        dY = nose[1] - eye_center[1]
        dX = nose[0] - eye_center[0]
        yaw = math.degrees(math.atan2(dX, dY))

        # Calculate pitch angle
        dY = ((left_eye[1] + right_eye[1]) * 0.5) - ((left_mouth[1] + right_mouth[1]) * 0.5)
        dX = ((left_eye[0] + right_eye[0]) * 0.5) - ((left_mouth[0] + right_mouth[0]) * 0.5)
        pitch = math.degrees(math.atan2(dY, dX))

        return roll, yaw, pitch

    attentive_faces = 0

    if len(location) > 0:
        for face in location:
            confidence = face['confidence']
            if confidence >= confidence_threshold:
                # Calculate angles
                roll, yaw, pitch = calculate_angles(face['keypoints'])

                # Check if the face is attentive based on yaw
                if -25 <= yaw <= 20:
                    attentive_faces += 1

                    # Draw bounding box and landmarks
                    x, y, width, height = face['box']
                    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
                    for key, point in face['keypoints'].items():
                        cv2.circle(frame, point, 2, (0, 255, 0), 2)

    return attentive_faces

def process_video(video_path, interval=5, process_duration=2, confidence_threshold=0.9, nth_frame=10):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval_frames = int(fps * interval)
    process_frames = int(fps * process_duration)

    frame_count = 0

    # Data collection for plotting
    times = []
    attentive_counts = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process only every nth frame
        if frame_count % nth_frame == 0:
            if frame_count % interval_frames < process_frames:
                attentive_faces = process_frame(frame, confidence_threshold)
                timestamp = frame_count / fps
                print(f"Number of attentive faces: {attentive_faces}, Time: {timestamp:.2f} seconds")

                # Collect data points
                times.append(timestamp)
                attentive_counts.append(attentive_faces)

        frame_count += 1

    cap.release()

    # Save attentiveness data to a JSON file
    attentiveness_data = {
        "times": times,
        "attentive_counts": attentive_counts
    }
    with open('attentiveness.json', 'w') as json_file:
        json.dump(attentiveness_data, json_file)

# Flask route to serve the attentiveness data
@app.route('/attentiveness', methods=['GET'])
def get_attentiveness():
    with open('attentiveness.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

# Flask route to display the chart
@app.route('/attentiveness-chart')
def attentiveness_chart():
    with open('attentiveness.json', 'r') as f:
        data = json.load(f)
    
    chart_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Attentiveness Chart</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <canvas id="attentivenessChart" width="800" height="400"></canvas>
        <script>
            const ctx = document.getElementById('attentivenessChart').getContext('2d');
            const times = {{ times | tojson }};
            const attentiveCounts = {{ attentive_counts | tojson }};

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: times,
                    datasets: [{
                        label: 'Number of Attentive Students',
                        data: attentiveCounts,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            type: 'linear',
                            position: 'bottom'
                        },
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        </script>
    </body>
    </html>
    """

    return render_template_string(chart_html, times=data["times"], attentive_counts=data["attentive_counts"])

# Function to run the Flask app
def run_flask_app():
    app.run(debug=True, use_reloader=False)

# Main function to process the video and start the Flask app
if __name__ == '__main__':
    video_path = '/Users/shauryan/Documents/UWINDSOR/SEM 2/ADT/ADT Project/CnCAP/Attentiveness/video.mov'  # Add your video path here

    # Process the video
    process_video(video_path, nth_frame=10)

    # Run the Flask app
    run_flask_app()
