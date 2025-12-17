import sqlite3
import json
import os
from datetime import datetime

DB_PATH = 'scan_history.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scans
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp TEXT, 
                  status TEXT, 
                  celery_id TEXT,
                  result TEXT)''')
    conn.commit()
    conn.close()

def add_scan(celery_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Used 'Running' as initial status
    c.execute("INSERT INTO scans (timestamp, status, celery_id, result) VALUES (?, ?, ?, ?)",
              (datetime.now().isoformat(), 'Running', celery_id, '{}'))
    scan_id = c.lastrowid
    conn.commit()
    conn.close()
    return scan_id

def update_scan_status(scan_id, status, result=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if result:
        c.execute("UPDATE scans SET status=?, result=? WHERE id=?", (status, json.dumps(result), scan_id))
    else:
        c.execute("UPDATE scans SET status=? WHERE id=?", (status, scan_id))
    conn.commit()
    conn.close()

def get_all_scans():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM scans ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_scan(scan_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM scans WHERE id=?", (scan_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None
