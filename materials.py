import storage
import engine

def get_material_inputs():
    items = []
    print("\n--- MATERIALS BREAKDOWN (Type 'done') ---")
    while True:
        name = input("Material Name: ").strip().title()
        if name.lower() == 'done': break
        if not name: continue
        try:
            est_cost = float(input(f"  Estimated Cost for {name} ($): "))
            items.append({"name": name, "estimated_cost": est_cost, "actual_cost": 0.0})
        except ValueError: 
            print("  !! Invalid number. Please retry.")
    return items

def log_materials_ui(selected_project, index):
    while True:
        print(f"\n--- LOG MATERIAL COSTS: {selected_project['Project']} ---")
        mats = selected_project.get('Materials', [])
        for i, m in enumerate(mats):
            print(f"{i+1}. {m['name']} (Spent so far: ${m.get('actual_cost', 0):,.2f})")
        
        choice = input("\nSelect Material # to log cost, 'N' for New Material, or '0' to exit: ").strip().upper()
        
        if choice == '0':
            break 
            
        elif choice == 'N':
            name = input("Enter new Material name: ").strip().title()
            is_billable = input("Is this a billable variation to the customer? (y/n): ").strip().lower()
            
            try:
                if is_billable == 'y':
                    est_cost = float(input(f"Enter estimated quote for {name} ($): "))
                    mats.append({"name": name, "estimated_cost": est_cost, "actual_cost": 0.0, "variation": True, "billable": True})
                    print(f">> Billable variation added. Project budget will increase.")
                else:
                    mats.append({"name": name, "estimated_cost": 0.0, "actual_cost": 0.0, "variation": True, "billable": False})
                    print(f">> Non-billable material added. This will track as a project variance (loss).")
                
                # Recalculate totals
                labor = selected_project.get('Labor', [])
                base = engine.calculate_totals(labor, mats)
                tax = engine.calculate_gst(base['total_ex'])
                
                selected_project['Total_Ex_GST'] = base['total_ex']
                selected_project['GST'] = tax['gst_value']
                selected_project['Total_Inc_GST'] = tax['total_inc_gst']
                
                storage.update_project(index, selected_project)
                
            except ValueError:
                print("!! Invalid input. Please try again.")
            
        elif choice.isdigit() and int(choice) > 0:
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