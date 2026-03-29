import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "analytics_bot.db"

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table for user profiles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            total_requests INTEGER DEFAULT 0,
            last_activity DATETIME
        )
    ''')
    
    # Table for detailed analysis history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sentiment_score REAL,
            timestamp DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(user_id, username):
    """Registers a new user or updates their activity count."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    cursor.execute('''
        UPDATE users 
        SET total_requests = total_requests + 1, 
            last_activity = ? 
        WHERE user_id = ?
    ''', (datetime.now(), user_id))
    conn.commit()
    conn.close()

def log_analysis(user_id, score):
    """Logs every single analysis result."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO analysis_logs (user_id, sentiment_score, timestamp) VALUES (?, ?, ?)', 
                   (user_id, score, datetime.now()))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    """Gets total requests for a specific user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT total_requests FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_leaderboard():
    """Gets top 5 most active users."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, total_requests 
        FROM users 
        ORDER BY total_requests DESC 
        LIMIT 5
    ''')
    leaders = cursor.fetchall()
    conn.close()
    return leaders

def get_full_history_df(user_id):
    """Fetches analysis history and returns it as a Pandas DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    query = f"SELECT timestamp, sentiment_score FROM analysis_logs WHERE user_id = {user_id} ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df