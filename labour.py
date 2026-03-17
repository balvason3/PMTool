import storage
import engine

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
    while True:
        print(f"\n--- LOG HOURS: {selected_project['Project']} ---")
        labor = selected_project.get('Labor', [])
        for i, l in enumerate(labor):
            print(f"{i+1}. {l['role']} (Current: {l.get('actual_hours', 0)} hrs)")
        
        choice = input("\nSelect Role # to log hours, 'N' for New Role, or '0' to exit: ").strip().upper()
        
        if choice == '0':
            break 
            
        elif choice == 'N':
            role = input("Enter new Role name: ").strip().title()
            try:
                rate = float(input(f"Enter hourly rate for {role} ($): "))
                is_billable = input("Is this a billable variation to the customer? (y/n): ").strip().lower()
                
                if is_billable == 'y':
                    est_hrs = float(input("Enter estimated hours for this variation: "))
                    labor.append({"role": role, "estimated_hours": est_hrs, "actual_hours": 0.0, "rate": rate, "variation": True, "billable": True})
                    print(f">> Billable variation added. Project budget will increase.")
                else:
                    labor.append({"role": role, "estimated_hours": 0.0, "actual_hours": 0.0, "rate": rate, "variation": True, "billable": False})
                    print(f">> Non-billable role added. This will track as a project variance (loss).")
                
                # Recalculate totals
                mats = selected_project.get('Materials', [])
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
            if idx < len(labor):
                try:
                    added = float(input(f"Add how many hours to {labor[idx]['role']}? "))
                    current = labor[idx].get('actual_hours', 0)
                    labor[idx]['actual_hours'] = current + added
                    storage.update_project(index, selected_project)
                    print(">> Hours Logged Successfully.")
                except ValueError:
                    print("!! Invalid number.")