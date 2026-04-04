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
    """Loads all data. Now correctly retains the internal_id and loads Notes."""
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
        
        labor, materials, notes = [], [], []
        
        for item in items:
            if item['item_type'] == 'Labor':
                labor.append(json.loads(item['item_data']))
            elif item['item_type'] == 'Material':
                materials.append(json.loads(item['item_data']))
            elif item['item_type'] == 'Note':
                notes.append(json.loads(item['item_data']))
                
        project_dict['Labor'] = labor
        project_dict['Materials'] = materials
        project_dict['Notes'] = notes
        
        # WE NO LONGER DELETE 'internal_id' - We need it for safe updates!
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
    """
    LEGACY WRAPPER: po_generator.py currently calls this to save batch updates.
    Instead of wiping the DB, it now safely updates each individual project.
    """
    for proj in history_list:
        update_project(None, proj)

def save_to_db(name, scope, client, target_date, labor, materials, total_ex, gst, total_inc):
    """TRUE SQL INSERT: Saves a brand new estimate directly to the database."""
    initialize_db()
    quote_id = generate_next_quote_id()    
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Insert the main project record
        cursor.execute('''
            INSERT INTO projects (Project_ID, Quote_Number, Status, Timestamp, Project, Client, Target_Date, Scope, Total_Ex_GST, GST, Total_Inc_GST)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            None, quote_id, "Draft", now, name, client, target_date, scope, total_ex, gst, total_inc
        ))
        
        # 2. Get the new internal_id so we can link the items
        internal_id = cursor.lastrowid
        
        # 3. Insert all nested items
        for l_item in labor:
            cursor.execute("INSERT INTO project_items (project_id, item_type, item_data) VALUES (?, ?, ?)", 
                           (internal_id, 'Labor', json.dumps(l_item)))
                           
        for m_item in materials:
            cursor.execute("INSERT INTO project_items (project_id, item_type, item_data) VALUES (?, ?, ?)", 
                           (internal_id, 'Material', json.dumps(m_item)))
                           
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"\n!! Database Save Error: {e}")
    finally:
        conn.close()

def update_project(index, updated_data):
    """TRUE SQL UPDATE: Modifies an existing record using its internal_id."""
    # We no longer care about the list 'index'. We use the SQLite primary key.
    internal_id = updated_data.get('internal_id')
    
    if not internal_id:
        print("!! Critical Error: Cannot update project without internal_id.")
        return

    initialize_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Convert empty strings to None to satisfy SQLite UNIQUE constraints
    job_val = updated_data.get('Project_ID')
    if job_val == "": job_val = None
    
    quote_val = updated_data.get('Quote_Number')
    if quote_val == "": quote_val = None

    try:
        # 1. Update the main project record
        cursor.execute('''
            UPDATE projects 
            SET Project_ID = ?, Quote_Number = ?, Status = ?, Timestamp = ?, Project = ?, Client = ?, Target_Date = ?, Scope = ?, Total_Ex_GST = ?, GST = ?, Total_Inc_GST = ?
            WHERE internal_id = ?
        ''', (
            job_val, quote_val, updated_data.get('Status', 'Draft'), updated_data.get('Timestamp', ''),
            updated_data.get('Project', ''), updated_data.get('Client', ''), updated_data.get('Target_Date', ''),
            updated_data.get('Scope', ''), updated_data.get('Total_Ex_GST', 0.0), updated_data.get('GST', 0.0),
            updated_data.get('Total_Inc_GST', 0.0), internal_id
        ))
        
        # 2. To handle items cleanly, we wipe only THIS project's items, then re-insert them.
        cursor.execute("DELETE FROM project_items WHERE project_id = ?", (internal_id,))
        
        for l_item in updated_data.get('Labor', []):
            cursor.execute("INSERT INTO project_items (project_id, item_type, item_data) VALUES (?, ?, ?)", 
                           (internal_id, 'Labor', json.dumps(l_item)))
                           
        for m_item in updated_data.get('Materials', []):
            cursor.execute("INSERT INTO project_items (project_id, item_type, item_data) VALUES (?, ?, ?)", 
                           (internal_id, 'Material', json.dumps(m_item)))

        for n_item in updated_data.get('Notes', []):
            cursor.execute("INSERT INTO project_items (project_id, item_type, item_data) VALUES (?, ?, ?)", 
                           (internal_id, 'Note', json.dumps(n_item)))
                           
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"\n!! Database Update Error: {e}")
    finally:
        conn.close()
        