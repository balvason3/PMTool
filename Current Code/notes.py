# --- PMTool: NOTES & ACTIVITY LOG MODULE ---
import storage
from datetime import datetime

def add_note_ui(selected_project, index):
    """Prompts the user for a note and saves it to the project."""
    print(f"\n--- LOG NOTE: {selected_project['Project']} ---")
    note_text = input("Enter your note (or '0' to cancel): ").strip()
    
    if note_text != '0' and note_text:
        now = datetime.now().strftime("%d-%m-%Y %H:%M")
        new_note = {"timestamp": now, "text": note_text}
        
        # Ensure the Notes array exists before appending
        if "Notes" not in selected_project:
            selected_project["Notes"] = []
            
        selected_project["Notes"].append(new_note)
        storage.update_project(index, selected_project)
        print(">> Note logged successfully.")