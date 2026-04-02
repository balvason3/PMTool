# --- BEDROCK: SQLITE DATABASE MODULE ---
import sqlite3
import os

DATA_DIR = 'data'
DB_FILE = os.path.join(DATA_DIR, 'bedrock.db')

def initialize_db():
    """Creates the SQLite database and tables if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. PROJECTS TABLE (Consolidated)
    # Added Quote_Number and standardized column names
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_no TEXT UNIQUE,
            quote_no TEXT UNIQUE, -- Used once accepted
            status TEXT DEFAULT 'Draft', -- Defaults to Draft for Estimates
            timestamp TEXT,
            project_name TEXT,
            client TEXT,
            target_date TEXT,
            scope TEXT,
            total_ex_gst REAL,
            gst REAL,
            total_inc_gst REAL
        )
    ''')

    # 2. LABOR TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS labor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            role TEXT,
            estimated_hours REAL,
            actual_hours REAL,
            rate REAL,
            markup_percent REAL,
            variation BOOLEAN,
            billable BOOLEAN,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    ''')

    # 3. MATERIALS TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            name TEXT,
            estimated_cost REAL,
            actual_cost REAL,
            markup_percent REAL,
            procurement_status TEXT DEFAULT 'Pending',
            supplier TEXT DEFAULT 'TBA',
            variation BOOLEAN,
            billable BOOLEAN,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    ''')

    # 4. NOTES TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            timestamp TEXT,
            text TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()