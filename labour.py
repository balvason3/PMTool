# --- PMTool: LABOUR MODULE ---

def get_labour_inputs():
    """Handles the loop to collect baseline estimates."""
    items = []
    print("\n--- LABOUR ESTIMATE (Baseline) ---")
    while True:
        role = input("Role (PM/Trade/Admin) or 'done': ").strip().title()
        if role.lower() == 'done': break
        try:
            hrs = float(input(f"  Estimated Hours for {role}: "))
            rate = float(input(f"  Hourly Rate for {role} ($): "))
            # We initialize actual_hours at 0.0 for the POC tracker
            items.append({
                "role": role, 
                "estimated_hours": hrs, 
                "actual_hours": 0.0, 
                "rate": rate
            })
        except ValueError:
            print("  !! Invalid number. Please retry.")
    return items

def log_actual_hours(project_data):
    """Business logic for updating the 'Actuals' without touching the Baseline."""
    print(f"\n--- LOGGING PROGRESS: {project_data['Project']} ---")
    labour_list = project_data.get('Labor', [])
    
    for i, l in enumerate(labour_list):
        print(f"{i+1}. {l['role']} (Spent: {l['actual_hours']}/{l['estimated_hours']} hrs)")
    
    choice = input("\nSelect role # to log hours (or '0' to cancel): ")
    if choice.isdigit() and int(choice) > 0:
        idx = int(choice) - 1
        added = float(input(f"Hours to add for {labour_list[idx]['role']}: "))
        labour_list[idx]['actual_hours'] += added
        return labour_list
    return None