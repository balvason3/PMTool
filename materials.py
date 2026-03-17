import storage

# --- Keep your existing get_material_inputs() function here ---
def get_material_inputs():
    items = []
    print("\n--- MATERIALS BREAKDOWN (Type 'done') ---")
    while True:
        name = input("Material Name: ").strip().title()
        if name.lower() == 'done': break
        try:
            est_cost = float(input(f"  Estimated Cost for {name} ($): "))
            items.append({"name": name, "estimated_cost": est_cost, "actual_cost": 0.0})
        except ValueError: 
            print("  !! Invalid number. Please retry.")
    return items

def log_materials_ui(selected_project, index):
    print(f"\n--- LOG MATERIAL COSTS: {selected_project['Project']} ---")
    mats = selected_project.get('Materials', [])
    for i, m in enumerate(mats):
        print(f"{i+1}. {m['name']} (Spent so far: ${m.get('actual_cost', 0):,.2f})")
    
    choice = input("\nSelect Material # to log cost (0 to cancel): ")
    if choice.isdigit() and int(choice) > 0:
        idx = int(choice) - 1
        if idx < len(mats):
            try:
                added = float(input(f"Log invoice amount for {mats[idx]['name']} ($): "))
                current = mats[idx].get('actual_cost', 0)
                mats[idx]['actual_cost'] = current + added
                storage.update_project(index, selected_project)
                print(">> Material Cost Logged Successfully.")
            except ValueError:
                print("!! Invalid number.")