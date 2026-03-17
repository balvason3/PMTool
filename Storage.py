import json
import os
from datetime import datetime

DB_FILE = 'projectBudgetDB.json'

# --- CONFIG (For future Settings Menu) ---
ID_PREFIX = "JN-"
START_NUMBER = 10000

def get_all_history():
    """Reads all projects and AUTO-MIGRATES old data to have Job Numbers."""
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

    # 1. Find the highest existing valid ID
    highest_id = START_NUMBER - 1
    for entry in history:
        pid = entry.get("Project_ID", "")
        if pid.startswith(ID_PREFIX):
            try:
                num = int(pid.replace(ID_PREFIX, ""))
                if num > highest_id:
                    highest_id = num
            except ValueError:
                continue

    # 2. Fix older projects (N/A) or broken ones (JN-0)
    for entry in history:
        pid = entry.get("Project_ID", "")
        # If it doesn't exist, is blank, or is the broken JN-0
        if not pid or pid == "N/A" or pid == "JN-0":
            highest_id += 1
            entry["Project_ID"] = f"{ID_PREFIX}{highest_id}"
            needs_save = True

    # 3. If we updated legacy data, save it permanently
    if needs_save:
        overwrite_db(history)

    return history

def generate_next_id(history):
    """Finds the next available Job Number based on the current history."""
    if not history:
        return f"{ID_PREFIX}{START_NUMBER}"

    highest = START_NUMBER - 1
    for entry in history:
        pid = entry.get("Project_ID", "")
        if pid.startswith(ID_PREFIX):
            try:
                num = int(pid.replace(ID_PREFIX, ""))
                if num > highest:
                    highest = num
            except ValueError:
                continue
                
    return f"{ID_PREFIX}{highest + 1}"

def overwrite_db(history_list):
    """Overwrites the entire file with a new list (used for Deleting/Editing)."""
    with open(DB_FILE, 'w') as f:
        for entry in history_list:
            json.dump(entry, f)
            f.write('\n')

def save_to_db(name, scope, labor, materials, total_ex, gst, total_inc):
    """Generates an ID and saves the new project."""
    history = get_all_history()
    project_id = generate_next_id(history) # Auto-Generate ID
    now = datetime.now()
    
    budget_data = {
        "Project_ID": project_id,
        "Timestamp": now.strftime("%d-%m-%Y %H:%M"),
        "Project": name,
        "Scope": scope,
        "Labor": labor,
        "Materials": materials,
        "Total_Ex_GST": total_ex,
        "GST": gst,
        "Total_Inc_GST": total_inc
    }
    
    # Append to our list and rewrite the file
    history.append(budget_data)
    overwrite_db(history)

def delete_project_by_index(index):
    """Removes a project at a specific position and updates the file."""
    history = get_all_history()
    if 0 <= index < len(history):
        removed_item = history.pop(index)
        overwrite_db(history)
        return removed_item['Project']
    return None
    
def update_project(index, updated_data):
    """Overwrites a specific project in the JSON file."""
    history = get_all_history()
    if 0 <= index < len(history):
        history[index] = updated_data
        overwrite_db(history)