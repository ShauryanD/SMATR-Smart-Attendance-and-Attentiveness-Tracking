from flask import Flask, request, jsonify
import json
import sqlite3

app = Flask(__name__)

def db_connection ():
    conn = None
    try:
        conn = sqlite3.connect('test.sqlite')
    except sqlite3.Error as e:
        print(e)
    return conn


@app.route('/test', methods = ['GET', 'POST'])
def getTestList():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'GET' :
        cursor = conn.execute("SELECT * FROM test")
        test_list = [
            dict(id=row[0], author=row[1], language=row[2], title=row[3])
            for row in cursor.fetchall()
        ]
        if test_list is not None:
            return jsonify(test_list)
    
    if request. method == 'POST':
        new_author = request.form['author']
        new_lang = request.form['language']
        new_title = request.form['title']

        query = """INSERT INTO test (author, language, title) 
                VALUES (?, ?, ?)"""
        cursor = conn.execute(query, (new_author, new_lang, new_title))
        conn.commit()
        last_id = cursor.lastrowid
        return f"Book added with id: {last_id} successfully!", 201

if __name__ == '__main__':
    app.run(debug=True)