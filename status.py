# --- PMTool: STATUS MODULE ---
import storage

def accept_quote_ui(selected_project, index):
    """Converts a Quoted estimate into an Active project."""
    print(f"\n--- ACCEPT QUOTE: {selected_project['Project']} ---")
    quote_no = input("Enter the signed Quote/Contract Number: ").strip()
    
    if quote_no:
        selected_project['Quote_Number'] = quote_no
        selected_project['Status'] = 'Active'
        storage.update_project(index, selected_project)
        print(f">> Success! Quote {quote_no} is now an ACTIVE project.")
    else:
        print("!! Quote Number is required to activate a project.")
        
        # In status.py

def convert_estimate_to_project(selected_project, index):
    """
    Triggers when a 'Quoted' estimate is accepted.
    Requires a Quote Number to move status to 'Active'.
    """
    print(f"\n--- ACCEPT QUOTE: {selected_project['Project']} ---")
    quote_number = input("Enter signed Quote Number: ").strip()
    
    if quote_number:
        selected_project['Quote_Number'] = quote_number
        selected_project['Status'] = 'Active'
        # Update in database using existing storage logic
        import storage
        storage.update_project(index, selected_project)
        print(f">> Success! Estimate converted to Active Project with Quote #{quote_number}.")
    else:
        print("!! A Quote Number is required to activate this project.")

def change_status_ui(selected_project, index):
    statuses = ["Draft", "Quoted", "Active", "Completed", "Invoiced", "Archived"]
    
    print(f"\n--- CHANGE STATUS: {selected_project['Project']} ---")
    print(f"Current Status: {selected_project.get('Status', 'Draft').upper()}")
    for i, s in enumerate(statuses):
        print(f"{i+1}. {s}")
        
    choice = input("\nSelect new status # (0 to cancel): ")
    if choice.isdigit() and 0 < int(choice) <= len(statuses):
        new_status = statuses[int(choice)-1]
        
        # --- THE KEY TRIGGER: Generate Job Number when moving to Active ---
        if new_status == "Active" and not selected_project.get('Project_ID'):
            new_job_no = storage.generate_next_id()
            selected_project['Project_ID'] = new_job_no
            print(f"\n>> CONGRATULATIONS! Estimate accepted. Assigned Job No: {new_job_no}")
            
        selected_project['Status'] = new_status
        storage.update_project(index, selected_project)
        print(f">> Project moved to: {new_status}")
        return new_status
        
    return selected_project.get('Status')