import sqlite3
import os
import json
from datetime import datetime
import settings

DATA_DIR = 'data'
DB_FILE = os.path.join(DATA_DIR, 'bedrock.db')

def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = 1")
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. CORE PROJECTS TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            internal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            Project_ID TEXT UNIQUE,
            Quote_Number TEXT UNIQUE,
            Status TEXT DEFAULT 'Draft',
            Timestamp TEXT,
            Project TEXT,
            Client TEXT,
            Target_Date TEXT,
            Scope TEXT,
            Total_Ex_GST REAL,
            GST REAL,
            Total_Inc_GST REAL
        )
    ''')
    
    # --- MIGRATIONS (Safe updates for existing databases) ---
    try:
        cursor.execute("ALTER TABLE projects ADD COLUMN Quote_Number TEXT UNIQUE")
    except sqlite3.OperationalError:
        pass # Column already exists, safe to ignore
    
    # 2. ITEMS TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            item_type TEXT,
            item_data TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(internal_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def get_all_history():
    initialize_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM projects")
    projects_data = cursor.fetchall()
    
    history = []
    for p in projects_data:
        project_dict = dict(p)
        
        cursor.execute("SELECT item_type, item_data FROM project_items WHERE project_id = ?", (p['internal_id'],))
        items = cursor.fetchall()
        
        labor, materials = [], []
        
        for item in items:
            if item['item_type'] == 'Labor':
                labor.append(json.loads(item['item_data']))
            elif item['item_type'] == 'Material':
                materials.append(json.loads(item['item_data']))
                
        project_dict['Labor'] = labor
        project_dict['Materials'] = materials
        del project_dict['internal_id']
        
        history.append(project_dict)
        
    conn.close()
    return history
    
def generate_next_quote_id():
    """Generates the next sequential Quote Number (e.g., QT-1000)."""
    initialize_db()
    config = settings.load_settings()
    prefix = config.get('quote_prefix', 'QT-')
    start_number = config.get('quote_start', 1000)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check against the correct Quote_Number column
    cursor.execute("SELECT Quote_Number FROM projects WHERE Quote_Number LIKE ?", (f"{prefix}%",))
    rows = cursor.fetchall()
    conn.close()
    
    highest = start_number - 1
    for row in rows:
        qid = row['Quote_Number']
        if qid:
            try:
                num = int(qid.replace(prefix, ""))
                if num > highest:
                    highest = num
            except ValueError:
                continue
                
    return f"{prefix}{highest + 1}"

def generate_next_id(history=None):
    """Generates the next sequential Job Number (e.g., JN-10000)."""
    initialize_db()
    config = settings.load_settings()
    id_prefix = config.get('id_prefix', 'JN-')
    start_number = config.get('start_number', 10000)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT Project_ID FROM projects WHERE Project_ID LIKE ?", (f"{id_prefix}%",))
    rows = cursor.fetchall()
    conn.close()
    
    highest = start_number - 1
    for row in rows:
        pid = row['Project_ID']
        if pid:
            try:
                num = int(pid.replace(id_prefix, ""))
                if num > highest:
                    highest = num
            except ValueError:
                continue
            
    return f"{id_prefix}{highest + 1}"

def overwrite_db(history_list):
    """THE SQL BRIDGE: Safely synchronizes your modified lists into the database."""
    initialize_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Wipe the slate clean to mirror your old JSON overwrite behavior
        cursor.execute("DELETE FROM projects")
        cursor.execute("DELETE FROM project_items")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='projects'")
        
        # 2. Re-insert all data natively into SQL
        for entry in history_list:
            
            # CRITICAL FIX: Convert empty strings "" to None (NULL in SQL)
            # This prevents the UNIQUE constraint crash.
            job_val = entry.get('Project_ID')
            if job_val == "": job_val = None
            
            quote_val = entry.get('Quote_Number')
            if quote_val == "": quote_val = None

            cursor.execute('''
                INSERT INTO projects (Project_ID, Quote_Number, Status, Timestamp, Project, Client, Target_Date, Scope, Total_Ex_GST, GST, Total_Inc_GST)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_val,
                quote_val,
                entry.get('Status', 'Draft'),
                entry.get('Timestamp', ''),
                entry.get('Project', ''),
                entry.get('Client', ''),
                entry.get('Target_Date', ''),
                entry.get('Scope', ''),
                entry.get('Total_Ex_GST', 0.0),
                entry.get('GST', 0.0),
                entry.get('Total_Inc_GST', 0.0)
            ))
            
            internal_id = cursor.lastrowid
            
            for l_item in entry.get('Labor', []):
                cursor.execute("INSERT INTO project_items (project_id, item_type, item_data) VALUES (?, ?, ?)", 
                               (internal_id, 'Labor', json.dumps(l_item)))
                               
            for m_item in entry.get('Materials', []):
                cursor.execute("INSERT INTO project_items (project_id, item_type, item_data) VALUES (?, ?, ?)", 
                               (internal_id, 'Material', json.dumps(m_item)))
                               
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"\n!! Database Save Error: {e}")
        print("!! The application tried to save duplicate IDs. Check your Job/Quote numbering.")
    finally:
        conn.close()

def save_to_db(name, scope, client, target_date, labor, materials, total_ex, gst, total_inc):
    """Saves a brand new estimate."""
    history = get_all_history()
    quote_id = generate_next_quote_id()    
    now = datetime.now()
    budget_data = {
        "Project_ID": "",                  # <-- BLANK until accepted (now correctly parses to None)
        "Quote_Number": quote_id,          
        "Status": "Draft",                 
        "Timestamp": now.strftime("%d-%m-%Y %H:%M"),
        "Project": name,
        "Client": client,
        "Target_Date": target_date,
        "Scope": scope,
        "Labor": labor,
        "Materials": materials,
        "Total_Ex_GST": total_ex,
        "GST": gst,
        "Total_Inc_GST": total_inc
    }
    history.append(budget_data)
    overwrite_db(history)

def update_project(index, updated_data):
    """Maintains compatibility with engine.py updates."""
    history = get_all_history()
    if 0 <= index < len(history):
        history[index] = updated_data
        overwrite_db(history)