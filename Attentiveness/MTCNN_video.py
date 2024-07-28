# import cv2
# from facenet_pytorch import MTCNN
# from flask import Flask, jsonify, render_template
# import threading
# import time
# import math

# app = Flask(__name__)

# mtcnn = MTCNN()
# data_points = []

# def customAngle(a, b, c):
#     ba = [a[0] - b[0], a[1] - b[1]]
#     bc = [c[0] - b[0], c[1] - b[1]]
#     dotProd = ba[0] * bc[0] + ba[1] * bc[1]
#     baValue = math.sqrt(ba[0]**2 + ba[1]**2)
#     bcValue = math.sqrt(bc[0]**2 + bc[1]**2)
#     cosAngle = dotProd / (baValue * bcValue)
#     angle = math.acos(cosAngle)
#     return math.degrees(angle)

# def validFace(detection, mtcnnConfidence):
#     bbox, landmarks, prob = detection
#     return prob > mtcnnConfidence

# def humanDetection(boundingBox, humanProb, mtcnnLandmarks, mtcnnConfidence):
#     detections = map(lambda x, y, z: (x, y, z), boundingBox, mtcnnLandmarks, humanProb)
#     humanDetected = filter(lambda detection: validFace(detection, mtcnnConfidence), detections)
#     return list(humanDetected)

# def calculateAngle(landmarks):
#     RightEyeAngle = customAngle(landmarks[0], landmarks[1], landmarks[2])
#     LeftEyeAngle = customAngle(landmarks[1], landmarks[0], landmarks[2])
#     return RightEyeAngle, LeftEyeAngle

# def predFacePose(frame, mtcnnConfidence=0.9):
#     boundingBox, humanProb, mtcnnLandmarks = mtcnn.detect(frame, landmarks=True)
#     if boundingBox is None or humanProb is None or mtcnnLandmarks is None:
#         return [], []

#     humanDetected = humanDetection(boundingBox, humanProb, mtcnnLandmarks, mtcnnConfidence)
#     if not humanDetected:
#         return [], []

#     humanBBox = [bbox for bbox, _, _ in humanDetected]
#     resultList = []

#     for bbox, landmarks, _ in humanDetected:
#         RightEyeAngle, LeftEyeAngle = calculateAngle(landmarks)
#         if 10 <= int(RightEyeAngle) < 65 and 10 <= int(LeftEyeAngle) < 65:
#             resultList.append('Attentive')
#         else:
#             resultList.append('Not Attentive')

#     return humanBBox, resultList

# def process_video(video_path, mtcnnConfidence, nth_frame):
#     cap = cv2.VideoCapture(video_path)
#     print(f"Video processing started at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

#     fps = cap.get(cv2.CAP_PROP_FPS)
#     if not fps or fps == 0.0:
#         fps = 30

#     frame_count = 0
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         timestamp = frame_count / fps

#         if frame_count % nth_frame == 0:
#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             boundingBox, resultList = predFacePose(frame_rgb, mtcnnConfidence)
#             if boundingBox and resultList:
#                 facesCount = len(resultList)
#                 attentiveCount = len([i for i in resultList if i == 'Attentive'])
#                 data_points.append({
#                     "timestamp": timestamp,
#                     "faces_count": facesCount,
#                     "attentive_count": attentiveCount
#                 })
#                 print(f"Timestamp: {timestamp:.2f} seconds")
#                 print(f"Number of detected faces = {facesCount}")
#                 print(f"Number of attentive faces = {attentiveCount}")

#         frame_count += 1

#     cap.release()
#     cv2.destroyAllWindows()

# @app.route('/data_points', methods=['GET'])
# def get_data_points():
#     return jsonify(data_points)

# @app.route('/')
# def home():
#     return render_template('index.html')

# if __name__ == '__main__':
#     video_thread = threading.Thread(target=process_video, args=('video.mov', 0.93, 30))
#     video_thread.start()
#     app.run(debug=True, use_reloader=False, port=5001)

import cv2
from facenet_pytorch import MTCNN
from flask import Flask, jsonify, render_template, request
import threading
import time
import math
from datetime import datetime
import sqlite3

app = Flask(__name__)

mtcnn = MTCNN()
data_points = []

def create_db():
    conn = sqlite3.connect('attentiveness.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attentiveness
                 (date TEXT, timestamp REAL, faces_count INTEGER, attentive_count INTEGER)''')
    conn.commit()
    conn.close()

def insert_data(date, timestamp, faces_count, attentive_count):
    conn = sqlite3.connect('attentiveness.db')
    c = conn.cursor()
    c.execute("INSERT INTO attentiveness (date, timestamp, faces_count, attentive_count) VALUES (?, ?, ?, ?)",
              (date, timestamp, faces_count, attentive_count))
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
        date = datetime.now().strftime('%Y-%m-%d')

        if frame_count % nth_frame == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boundingBox, resultList = predFacePose(frame_rgb, mtcnnConfidence)
            if boundingBox and resultList:
                facesCount = len(resultList)
                attentiveCount = len([i for i in resultList if i == 'Attentive'])
                insert_data(date, timestamp, facesCount, attentiveCount)
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
    c = conn.cursor()
    c.execute("SELECT timestamp, faces_count, attentive_count FROM attentiveness WHERE date = ?", (date,))
    data = c.fetchall()
    conn.close()
    return jsonify([{"timestamp": row[0], "faces_count": row[1], "attentive_count": row[2]} for row in data])

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    create_db()
    video_thread = threading.Thread(target=process_video, args=('video.mov', 0.93, 30))
    video_thread.start()
    app.run(debug=True, use_reloader=False, port=5001)
