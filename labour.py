import storage

# --- Keep your existing get_labour_inputs() function here ---
def get_labour_inputs():
    items = []
    print("\n--- LABOUR ESTIMATE (Baseline) ---")
    while True:
        role = input("Role (PM/Trade/Admin) or 'done': ").strip().title()
        if role.lower() == 'done': break
        try:
            hrs = float(input(f"  Estimated Hours for {role}: "))
            rate = float(input(f"  Hourly Rate for {role} ($): "))
            items.append({"role": role, "estimated_hours": hrs, "actual_hours": 0.0, "rate": rate})
        except ValueError:
            print("  !! Invalid number. Please retry.")
    return items

def log_hours_ui(selected_project, index):
    print(f"\n--- LOG HOURS: {selected_project['Project']} ---")
    labor = selected_project.get('Labor', [])
    for i, l in enumerate(labor):
        print(f"{i+1}. {l['role']} (Current: {l.get('actual_hours', 0)} hrs)")
    
    choice = input("\nSelect Role # to log hours (0 to cancel): ")
    if choice.isdigit() and int(choice) > 0:
        idx = int(choice) - 1
        if idx < len(labor):
            try:
                added = float(input(f"Add how many hours to {labor[idx]['role']}? "))
                current = labor[idx].get('actual_hours', 0)
                labor[idx]['actual_hours'] = current + added
                storage.update_project(index, selected_project)
                print(">> Hours Logged Successfully.")
            except ValueError:
                print("!! Invalid number.")