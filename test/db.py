import os
import sqlite3

def populate_db():
    conn = sqlite3.connect('test.sqlite')
    cursor = conn.cursor()

    lfw_path = '/path/to/lfw-deepfunneled'

    for root, dirs, files in os.walk(lfw_path):
        for file in files:
            if file.endswith('.jpg'):
                name = root.split('/')[-1]
                student_id = file.split('.')[0]
                image_path = os.path.join(root, file)
                cursor.execute("INSERT INTO students (name, student_id, image_path) VALUES (?, ?, ?)",
                               (name, student_id, image_path))

    conn.commit()
    cursor.close()
    conn.close()

populate_db()
