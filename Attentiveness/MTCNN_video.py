import cv2
from facenet_pytorch import MTCNN
from flask import Flask, jsonify, request, render_template
import threading
import time
import math
import sqlite3

app = Flask(__name__)

mtcnn = MTCNN()
data_points = []

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('attentiveness.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attentiveness (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            date TEXT,
            faces_count INTEGER,
            attentive_count INTEGER,
            attentive_percentage REAL
        )
    ''')
    conn.commit()
    conn.close()

# Insert data into the SQLite database
def insert_data(timestamp, date, faces_count, attentive_count, attentive_percentage):
    conn = sqlite3.connect('attentiveness.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO attentiveness (timestamp, date, faces_count, attentive_count, attentive_percentage)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, date, faces_count, attentive_count, attentive_percentage))
    conn.commit()
    conn.close()

def customAngle(a, b, c):
    ba = [a[0] - b[0], a[1] - b[1]]
    bc = [c[0] - b[0], c[1] - b[1]]
    dotProd = ba[0] * bc[0] + ba[1] * bc[1]
    baValue = math.sqrt(ba[0]**2 + ba[1]**2)
    bcValue = math.sqrt(bc[0]**2 + bc[1]**2)
    cosAngle = dotProd / (baValue * bcValue)
    angle = math.acos(cosAngle)
    return math.degrees(angle)

def validFace(detection, mtcnnConfidence):
    bbox, landmarks, prob = detection
    return prob > mtcnnConfidence

def humanDetection(boundingBox, humanProb, mtcnnLandmarks, mtcnnConfidence):
    detections = map(lambda x, y, z: (x, y, z), boundingBox, mtcnnLandmarks, humanProb)
    humanDetected = filter(lambda detection: validFace(detection, mtcnnConfidence), detections)
    return list(humanDetected)

def calculateAngle(landmarks):
    RightEyeAngle = customAngle(landmarks[0], landmarks[1], landmarks[2])
    LeftEyeAngle = customAngle(landmarks[1], landmarks[0], landmarks[2])
    return RightEyeAngle, LeftEyeAngle

def predFacePose(frame, mtcnnConfidence=0.9):
    boundingBox, humanProb, mtcnnLandmarks = mtcnn.detect(frame, landmarks=True)
    if boundingBox is None or humanProb is None or mtcnnLandmarks is None:
        return [], []

    humanDetected = humanDetection(boundingBox, humanProb, mtcnnLandmarks, mtcnnConfidence)
    if not humanDetected:
        return [], []

    humanBBox = [bbox for bbox, _, _ in humanDetected]
    resultList = []

    for bbox, landmarks, _ in humanDetected:
        RightEyeAngle, LeftEyeAngle = calculateAngle(landmarks)
        if 10 <= int(RightEyeAngle) < 65 and 10 <= int(LeftEyeAngle) < 65:
            resultList.append('Attentive')
        else:
            resultList.append('Not Attentive')

    return humanBBox, resultList

def process_video(video_path, mtcnnConfidence, nth_frame):
    cap = cv2.VideoCapture(video_path)
    print(f"Video processing started at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps == 0.0:
        fps = 30

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        timestamp = frame_count / fps
        date = time.strftime('%Y-%m-%d', time.localtime())

        if frame_count % nth_frame == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boundingBox, resultList = predFacePose(frame_rgb, mtcnnConfidence)
            if boundingBox and resultList:
                facesCount = len(resultList)
                attentiveCount = len([i for i in resultList if i == 'Attentive'])
                attentivePercentage = (attentiveCount / facesCount) * 100 if facesCount > 0 else 0
                insert_data(timestamp, date, facesCount, attentiveCount, attentivePercentage)
                data_points.append({
                    "timestamp": timestamp,
                    "faces_count": facesCount,
                    "attentive_count": attentiveCount
                })
                print(f"Timestamp: {timestamp:.2f} seconds")
                print(f"Number of detected faces = {facesCount}")
                print(f"Number of attentive faces = {attentiveCount}")

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

@app.route('/data_points', methods=['GET'])
def get_data_points():
    date = request.args.get('date')
    conn = sqlite3.connect('attentiveness.db')
    cursor = conn.cursor()
    if date:
        cursor.execute("SELECT timestamp, faces_count, attentive_count FROM attentiveness WHERE date = ?", (date,))
    else:
        cursor.execute("SELECT timestamp, faces_count, attentive_count FROM attentiveness")
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    video_thread = threading.Thread(target=process_video, args=('video.mov', 0.93, 30))
    video_thread.start()
    app.run(debug=True, use_reloader=False, port=5001)
