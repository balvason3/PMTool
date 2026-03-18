import json
import os
from datetime import datetime
import settings

DB_FILE = 'projectBudgetDB.json'

def get_all_history():
    config = settings.load_settings()
    id_prefix = config['id_prefix']
    start_number = config['start_number']
    
    history = []
    needs_save = False
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        history.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

    highest_id = start_number - 1
    for entry in history:
        pid = entry.get("Project_ID", "")
        if pid.startswith(id_prefix):
            try:
                num = int(pid.replace(id_prefix, ""))
                if num > highest_id:
                    highest_id = num
            except ValueError:
                continue

    for entry in history:
        pid = entry.get("Project_ID", "")
        if not pid or pid == "N/A" or pid == f"{id_prefix}0":
            highest_id += 1
            entry["Project_ID"] = f"{id_prefix}{highest_id}"
            needs_save = True
            
        # NEW: Auto-migrate old projects to have an Active status
        if "Status" not in entry:
            entry["Status"] = "Active"
            needs_save = True

    if needs_save:
        overwrite_db(history)

    return history

def generate_next_id(history):
    config = settings.load_settings()
    id_prefix = config['id_prefix']
    start_number = config['start_number']
    
    if not history: return f"{id_prefix}{start_number}"
    highest = start_number - 1
    for entry in history:
        pid = entry.get("Project_ID", "")
        if pid.startswith(id_prefix):
            try:
                num = int(pid.replace(id_prefix, ""))
                if num > highest: highest = num
            except ValueError: continue
    return f"{id_prefix}{highest + 1}"

def overwrite_db(history_list):
    with open(DB_FILE, 'w') as f:
        for entry in history_list:
            json.dump(entry, f)
            f.write('\n')

def save_to_db(name, scope, client, target_date, labor, materials, total_ex, gst, total_inc):
    history = get_all_history()
    project_id = generate_next_id(history)
    now = datetime.now()
    budget_data = {
        "Project_ID": project_id,
        "Status": "Active", 
        "Timestamp": now.strftime("%d-%m-%Y %H:%M"),
        "Project": name,
        "Client": client,             # NEW
        "Target_Date": target_date,   # NEW
        "Scope": scope,
        "Labor": labor,
        "Materials": materials,
        "Total_Ex_GST": total_ex,
        "GST": gst,
        "Total_Inc_GST": total_inc
    }
    history.append(budget_data)
    overwrite_db(history)

def archive_project_by_index(index):
    """Changes a project's status instead of deleting it."""
    history = get_all_history()
    if 0 <= index < len(history):
        history[index]["Status"] = "Archived"
        overwrite_db(history)
        return history[index]['Project']
    return None
    
def restore_project_by_index(index):
    """Changes a project's status back to Active."""
    history = get_all_history()
    if 0 <= index < len(history):
        history[index]["Status"] = "Active"
        overwrite_db(history)
        return history[index]['Project']
    return None
    
def update_project(index, updated_data):
    history = get_all_history()
    if 0 <= index < len(history):
        history[index] = updated_data
        overwrite_db(history)