from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = "/data/submissions.db"

# 初始化数据库
def init_db():
    if not os.path.exists("/data"):
        os.makedirs("/data")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            submission_id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            poster_filename TEXT,
            status TEXT DEFAULT 'PROCESSING',
            result_note TEXT DEFAULT 'Waiting for processing',
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# API1: 创建提交记录
@app.route('/api/submission/create', methods=['POST'])
def create_submission():
    data = request.get_json()
    required_fields = ['submission_id', 'title', 'description', 'poster_filename']
    for field in required_fields:
        if field not in data:
            return jsonify({"code": 400, "msg": "Missing required fields"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO submissions (submission_id, title, description, poster_filename)
        VALUES (?, ?, ?, ?)
    ''', (data['submission_id'], data['title'], data['description'], data['poster_filename']))
    conn.commit()
    conn.close()
    return jsonify({"code": 200, "msg": "Submission created", "submission_id": data['submission_id']}), 200

# API2: 查询提交记录
@app.route('/api/submission/<submission_id>', methods=['GET'])
def get_submission(submission_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM submissions WHERE submission_id = ?', (submission_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"code": 404, "msg": "Submission not found"}), 404
    return jsonify({"code": 200, "data": dict(row)}), 200

# API3: 更新提交结果
@app.route('/api/submission/update', methods=['POST'])
def update_submission():
    data = request.get_json()
    required_fields = ['submission_id', 'status', 'result_note']
    for field in required_fields:
        if field not in data:
            return jsonify({"code": 400, "msg": "Missing required fields"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE submissions 
        SET status = ?, result_note = ?, update_time = CURRENT_TIMESTAMP
        WHERE submission_id = ?
    ''', (data['status'], data['result_note'], data['submission_id']))
    conn.commit()
    conn.close()
    return jsonify({"code": 200, "msg": "Submission updated"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)