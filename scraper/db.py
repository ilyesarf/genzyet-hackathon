import sqlite3
import datetime
import json
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            url TEXT,
            category TEXT,
            facebook_page_id TEXT,
            enabled BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM sources')
    if cursor.fetchone()[0] == 0:
        _seed_sources_from_json(cursor)
        
    conn.commit()
    conn.close()

def _seed_sources_from_json(cursor):
    sources_file = os.path.join(os.path.dirname(__file__), 'sources.json')
    if os.path.exists(sources_file):
        try:
            with open(sources_file, 'r') as f:
                sources = json.load(f)
            for source in sources:
                cursor.execute('''
                    INSERT INTO sources (name, type, url, category, facebook_page_id, enabled)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    source.get('name'),
                    source.get('type'),
                    source.get('url'),
                    source.get('category'),
                    source.get('facebook_page_id'),
                    1 if source.get('enabled', True) else 0
                ))
        except Exception as e:
            print(f"Error seeding sources: {e}")

def get_all_sources():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sources")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_source_by_id(source_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sources WHERE id = ?", (source_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_source(name, stype, url, category, facebook_page_id=None, enabled=True):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO sources (name, type, url, category, facebook_page_id, enabled)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, stype, url, category, facebook_page_id, 1 if enabled else 0))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error inserting source: {e}")
        raise
    finally:
        conn.close()

def toggle_source(source_id, enabled):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE sources SET enabled = ? WHERE id = ?
        ''', (1 if enabled else 0, source_id))
        conn.commit()
        if cursor.rowcount == 0:
            return False
        return True
    except Exception as e:
        print(f"Error toggling source: {e}")
        raise
    finally:
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

def clear_articles():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles")
    conn.commit()
    conn.close()

def delete_articles_by_source(source_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles WHERE source = ?", (source_name,))
    conn.commit()
    conn.close()

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
