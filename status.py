# --- PMTool: STATUS MODULE ---
import storage

def change_status_ui(selected_project, index):
    """Handles the lifecycle progression of a project."""
    statuses = ["Draft", "Quoted", "Active", "Completed", "Invoiced", "Archived"]
    
    print(f"\n--- CHANGE STATUS: {selected_project['Project']} ---")
    print(f"Current Status: {selected_project.get('Status', 'Active').upper()}")
    for i, s in enumerate(statuses):
        print(f"{i+1}. {s}")
        
    choice = input("\nSelect new status # (0 to cancel): ")
    if choice.isdigit() and 0 < int(choice) <= len(statuses):
        new_status = statuses[int(choice)-1]
        selected_project['Status'] = new_status
        storage.update_project(index, selected_project)
        print(f">> Project moved to: {new_status}")
        return new_status
    return selected_project.get('Status')