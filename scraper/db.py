import sqlite3
import datetime
import os

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_FILE = os.path.join(DB_DIR, "news.db")
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            url TEXT UNIQUE,
            title TEXT,
            body TEXT,
            category TEXT,
            published_at DATETIME,
            scraped_at DATETIME
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_published_at ON articles(published_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON articles(category)')
    conn.commit()
    conn.close()

def get_articles(window_hours=24, category=None):
    conn = get_db()
    cursor = conn.cursor()
    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(hours=window_hours)
    
    query = "SELECT * FROM articles WHERE published_at >= ?"
    params = [cutoff_time]
    
    if category:
        query += " AND category = ?"
        params.append(category)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def prune_old_articles():
    conn = get_db()
    cursor = conn.cursor()
    # Delete articles scraped more than 72 hours ago
    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(hours=72)
    cursor.execute("DELETE FROM articles WHERE scraped_at < ?", (cutoff_time,))
    conn.commit()
    conn.close()

def insert_article(source, url, title, body, category, published_at):
    conn = get_db()
    cursor = conn.cursor()
    scraped_at = datetime.datetime.utcnow()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO articles (source, url, title, body, category, published_at, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (source, url, title, body, category, published_at, scraped_at))
        conn.commit()
    except Exception as e:
        print(f"Error inserting article: {e}")
    finally:
        conn.close()

# Initialize the database on import
init_db()
