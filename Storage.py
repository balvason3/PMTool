import json
import os

# --- PMTool: STORAGE MODULE ---
# This handles the "Database" (JSON file) operations.

DB_FILE = 'projectBudgetDB.json'

def save_to_db(project_name, total_ex, gst, total_inc):
    """Saves a single project record to the JSON file."""
    budget_data = {
        "Project": project_name,
        "Total_Ex_GST": total_ex,
        "GST": gst,
        "Total_Inc_GST": total_inc
    }
    with open(DB_FILE, 'a') as f:
        json.dump(budget_data, f)
        f.write('\n')

def get_all_history():
    """Reads all projects from the file and returns them as a list of dictionaries."""
    history = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        history.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return history

def overwrite_db(history_list):
    """Overwrites the entire file with a new list (used for Deleting/Editing)."""
    with open(DB_FILE, 'w') as f:
        for entry in history_list:
            json.dump(entry, f)
            f.write('\n')

def delete_project_by_index(index):
    """Removes a project at a specific position and updates the file."""
    history = get_all_history()
    if 0 <= index < len(history):
        removed_item = history.pop(index)
        overwrite_db(history)
        return removed_item['Project']
    return None