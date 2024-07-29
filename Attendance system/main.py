# import threading
# import face_recognition
# import cv2
# import os
# import sqlite3
# from datetime import datetime, timedelta
# from PIL import Image
# import numpy as np
# from flask import Flask, request, jsonify, render_template
# import requests

# # Flask API Setup
# app = Flask(__name__)

# def db_connection():
#     conn = sqlite3.connect('attendance.db')
#     return conn

# @app.route('/attendance', methods=['GET'])
# def get_attendance():
#     conn = db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM attendance")
#     rows = cursor.fetchall()
#     conn.close()
#     return jsonify(rows)

# @app.route('/')
# def home():
#     response = requests.get('http://127.0.0.1:5000/attendance')  # Ensure this URL matches your Flask API
#     data = response.json()
#     return render_template('index.html', data=data)

# # Function to run the Flask app
# def run_flask_app():
#     app.run(debug=True, use_reloader=False)

# # Attendance Tracker Function
# def run_attendance_tracker():
#     # Load the known faces and names
#     known_face_encodings = []
#     known_face_names = []

#     dataset_path = "dataset"
#     for filename in os.listdir(dataset_path):
#         if filename.endswith(".jpg"):
#             image_path = os.path.join(dataset_path, filename)
#             try:
#                 # Open the image file
#                 with Image.open(image_path) as img:
#                     # Convert image to RGB format if it's not already in that format
#                     rgb_image = img.convert("RGB")
#                     # Convert the PIL image to a numpy array
#                     image = np.array(rgb_image)
#                     if image.ndim == 3 and image.shape[2] == 3:  # Ensure the image is 8-bit RGB
#                         # Process the image with face_recognition
#                         face_encodings = face_recognition.face_encodings(image)
#                         if face_encodings:  # Check if face encodings are found
#                             face_encoding = face_encodings[0]
#                             known_face_encodings.append(face_encoding)
#                             known_face_names.append(os.path.splitext(filename)[0])
#                         else:
#                             print(f"No face encodings found in image: {filename}")
#                     else:
#                         print(f"Image {filename} is not in 8-bit RGB format")
#             except Exception as e:
#                 print(f"Error processing file {filename}: {e}")

#     # Initialize variables
#     face_locations = []
#     face_encodings = []
#     face_names = []

#     # Create or connect to SQLite database
#     conn = sqlite3.connect('attendance.db')
#     cursor = conn.cursor()

#     # Create table if it doesn't exist
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS attendance (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT,
#             date TEXT,
#             time TEXT,
#             class TEXT
#         )
#     ''')

#     # Attendance interval
#     attendance_interval = timedelta(hours=1)

#     # Function to log attendance
#     def log_attendance(name):
#         if name == "Unknown":
#             return
        
#         now = datetime.now()
#         date = now.strftime("%Y-%m-%d")
#         time = now.strftime("%H:%M:%S")

#         cursor.execute("SELECT MAX(date || ' ' || time) FROM attendance WHERE name=?", (name,))
#         last_attendance = cursor.fetchone()[0]

#         if last_attendance:
#             last_attendance_time = datetime.strptime(last_attendance, '%Y-%m-%d %H:%M:%S')
#             if now - last_attendance_time >= attendance_interval:
#                 cursor.execute("INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)", (name, date, time))
#                 conn.commit()
#         else:
#             cursor.execute("INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)", (name, date, time))
#             conn.commit()

#     # Open a video file
#     video_path = "/Users/shauryan/Documents/UWINDSOR/SEM 2/ADT/ADT Project/CnCAP/SMATR-Smart-Attendance-and-Attentiveness-Tracking/Attentiveness/video.mov"  # Change this to your video file path
#     video_capture = cv2.VideoCapture(video_path)

#     while video_capture.isOpened():
#         ret, frame = video_capture.read()
#         if not ret:
#             break
        
#         # Convert the frame to RGB format
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
#         # Resize frame for faster processing
#         small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
        
#         # Find all the faces and face encodings in the current frame
#         face_locations = face_recognition.face_locations(small_frame)
#         face_encodings = face_recognition.face_encodings(small_frame, face_locations)
        
#         face_names = []
#         for face_encoding in face_encodings:
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
#             name = "Unknown"
            
#             face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#             best_match_index = min(range(len(face_distances)), key=face_distances.__getitem__)
#             if matches[best_match_index]:
#                 name = known_face_names[best_match_index]
            
#             face_names.append(name)
#             log_attendance(name)

#     video_capture.release()
#     cv2.destroyAllWindows()

#     # Close the database connection
#     conn.close()

# # Main function to start all threads
# if __name__ == '__main__':
#     flask_thread = threading.Thread(target=run_flask_app)
#     tracker_thread = threading.Thread(target=run_attendance_tracker)

#     flask_thread.start()
#     tracker_thread.start()

#     flask_thread.join()
#     tracker_thread.join()

import threading
import face_recognition
import cv2
import os
import sqlite3
from datetime import datetime, timedelta
from PIL import Image
import numpy as np
from flask import Flask, request, jsonify, render_template
import requests

# Flask API Setup
app = Flask(__name__)

def db_connection():
    conn = sqlite3.connect('attendance.db')
    return conn

@app.route('/attendance', methods=['GET'])
def get_attendance():
    date = request.args.get('date')
    class_name = request.args.get('class')
    
    query = "SELECT name, class, date FROM attendance WHERE 1=1"
    params = []
    
    if date:
        query += " AND date = ?"
        params.append(date)
        
    if class_name:
        query += " AND class = ?"
        params.append(class_name)
        
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify(rows)

@app.route('/')
def home():
    response = requests.get('http://127.0.0.1:5000/attendance')
    data = response.json()
    return render_template('index.html', data=data)

# Function to run the Flask app
def run_flask_app():
    app.run(debug=True, use_reloader=False)

# Attendance Tracker Function
def run_attendance_tracker():
    # Load the known faces and names
    known_face_encodings = []
    known_face_names = []

    dataset_path = "dataset"
    for filename in os.listdir(dataset_path):
        if filename.endswith(".jpg"):
            image_path = os.path.join(dataset_path, filename)
            try:
                # Open the image file
                with Image.open(image_path) as img:
                    # Convert image to RGB format if it's not already in that format
                    rgb_image = img.convert("RGB")
                    # Convert the PIL image to a numpy array
                    image = np.array(rgb_image)
                    if image.ndim == 3 and image.shape[2] == 3:  # Ensure the image is 8-bit RGB
                        # Process the image with face_recognition
                        face_encodings = face_recognition.face_encodings(image)
                        if face_encodings:  # Check if face encodings are found
                            face_encoding = face_encodings[0]
                            known_face_encodings.append(face_encoding)
                            known_face_names.append(os.path.splitext(filename)[0])
                        else:
                            print(f"No face encodings found in image: {filename}")
                    else:
                        print(f"Image {filename} is not in 8-bit RGB format")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    # Initialize variables
    face_locations = []
    face_encodings = []
    face_names = []

    # Create or connect to SQLite database
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            time TEXT,
            class TEXT
        )
    ''')

    # Attendance interval
    attendance_interval = timedelta(hours=1)

    # Function to log attendance
    def log_attendance(name, class_name):
        if name == "Unknown":
            return

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        cursor.execute("SELECT MAX(date || ' ' || time) FROM attendance WHERE name=? AND class=?", (name, class_name))
        last_attendance = cursor.fetchone()[0]

        if last_attendance:
            last_attendance_time = datetime.strptime(last_attendance, '%Y-%m-%d %H:%M:%S')
            if now - last_attendance_time >= attendance_interval:
                cursor.execute("INSERT INTO attendance (name, date, time, class) VALUES (?, ?, ?, ?)", (name, date, time, class_name))
                conn.commit()
        else:
            cursor.execute("INSERT INTO attendance (name, date, time, class) VALUES (?, ?, ?, ?)", (name, date, time, class_name))
            conn.commit()

    # Open a video file
    video_path = "video.mov"  # Change this to your video file path
    video_capture = cv2.VideoCapture(video_path)

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break
        
        # Convert the frame to RGB format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize frame for faster processing
        small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
        
        # Find all the faces and face encodings in the current frame
        face_locations = face_recognition.face_locations(small_frame)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)
        
        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"
            
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            
            face_names.append(name)
            log_attendance(name, "Class 2")  # Assuming "Class 1", update this as necessary

    video_capture.release()
    cv2.destroyAllWindows()

    # Close the database connection
    conn.close()

# Main function to start all threads
if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask_app)
    tracker_thread = threading.Thread(target=run_attendance_tracker)

    flask_thread.start()
    tracker_thread.start()

    flask_thread.join()
    tracker_thread.join()
