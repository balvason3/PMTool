import engine
import storage
import labour  

def get_labor_inputs():
    items = []
    print("\n--- LABOR BREAKDOWN (Type 'done') ---")
    while True:
        role = input("Role: ").strip().title()
        if role.lower() == 'done': break
        try:
            hrs = float(input(f"  Hours for {role}: "))
            rate = float(input(f"  Rate for {role} ($): "))
            # Initializing with actual_hours: 0 for new projects
            items.append({"role": role, "estimated_hours": hrs, "actual_hours": 0.0, "rate": rate})
        except ValueError: print("  !! Invalid number.")
    return items

def get_material_inputs():
    items = []
    print("\n--- MATERIALS BREAKDOWN (Type 'done') ---")
    while True:
        name = input("Material Name: ").strip().title()
        if name.lower() == 'done': break
        try:
            price = float(input(f"  Cost for {name} ($): "))
            items.append({"name": name, "price": price})
        except ValueError: print("  !! Invalid number.")
    return items

def create_estimate():
    name = input("Project Name: ")
    scope = input("Scope: ")
    labor = get_labor_inputs()
    mats = get_material_inputs()
    base = engine.calculate_totals(labor, mats)
    tax = engine.calculate_gst(base['total_ex'])
    storage.save_to_db(name, scope, labor, mats, base['total_ex'], tax['gst_value'], tax['total_inc_gst'])
    print("\n>> Saved.")

def view_history_menu():
    while True:
        logs = storage.get_all_history()
        if not logs:
            print("\nNo records found.")
            input("Press Enter to return...")
            break
        
        print("\n" + "-"*45)
        print(f"{'#':<3} | {'Project Name':<20} | {'Total (Inc)'}")
        print("-"*45)
        
        for i, entry in enumerate(logs, 1):
            total_inc = entry.get('Total_Inc_GST', 0)
            print(f"{i:<3} | {entry['Project']:<20} | ${total_inc:,.2f}")
        
        print("-"*45)

        choice = input("Select # for details (0 to exit): ")
        if choice == '0': break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(logs):
                selected = logs[idx]
                print("\n" + "="*75)
                print(f"PROJECT: {selected['Project'].upper()} | DATE: {selected.get('Timestamp', 'N/A')}")
                print(f"SCOPE: {selected.get('Scope', 'N/A')}")
                print("-" * 75)
                
                # --- DETAILED LABOR & FINANCIAL TRACKER ---
                print(f"{'Role':<12} | {'Orig Hr':>7} | {'Used':>5} | {'Rem Hr':>6} | {'Rem $':>12} | {'Var $':>10}")
                print("-" * 75)
                
                labor_data = selected.get('Labor', [])
                total_orig_val = 0
                total_rem_val = 0
                total_var_val = 0

                for l in labor_data:
                    orig = l.get('estimated_hours', l.get('hours', 0))
                    used = l.get('actual_hours', 0)
                    rate = l.get('rate', 0)
                    
                    rem_hrs = orig - used
                    # Financials
                    rem_cost = max(0, rem_hrs * rate)
                    var_cost = (used - orig) * rate if used > orig else 0.0
                    
                    total_orig_val += (orig * rate)
                    total_rem_val += rem_cost
                    total_var_val += var_cost

                    print(f"{l['role']:<12} | {orig:>7.1f} | {used:>5.1f} | {rem_hrs:>6.1f} | ${rem_cost:>11,.2f} | ${var_cost:>9,.2f}")
                
                print("-" * 75)
                print(f"{'LABOR TOTALS':<12} | {'':>7} | {'':>5} | {'':>6} | ${total_rem_val:>11,.2f} | ${total_var_val:>9,.2f}")
                
                # Show Materials
                print("\n" + f"{'Material Item':<58} | {'Cost':>12}")
                print("-" * 75)
                for m in selected.get('Materials', []):
                    print(f"{m['name']:<58} | ${m['price']:11,.2f}")
                
                print("=" * 75)
                print(f"{'Original Labor Budget:':<58} | ${total_orig_val:>11,.2f}")
                print(f"{'Remaining Labor Budget:':<58} | ${total_rem_val:>11,.2f}")
                if total_var_val > 0:
                    print(f"{'LABOR OVERRUN (LOSS):':<58} | ${total_var_val:>11,.2f}")
                print("-" * 75)
                print(f"{'GRAND TOTAL (Inc GST):':<58} | ${selected.get('Total_Inc_GST', 0):11,.2f}")
                print("=" * 75)
                
                print("\n1. Delete | 2. Back | 3. Log Hours")
                action = input("Choice: ")
                if action == '1':
                    if input("Confirm Delete? (y/n): ").lower() == 'y':
                        storage.delete_project_by_index(idx)
                        break
                elif action == '3':
                    log_hours_ui(selected, idx)
            else:
                print("!! Invalid Selection.")
        except ValueError:
            print("!! Please enter a number.")

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

def main_menu():
    while True:
        print("\n" + "="*40)
        print("   PMTool: MAIN MENU (Modular)   ")
        print("="*40)
        print("1. Create New Estimate")
        print("2. Manage History")
        print("3. EXIT")
        
        choice = input("\nSelect: ")

        if choice == '1':
            create_estimate()
        elif choice == '2':
            view_history_menu()
        elif choice == '3':
            print("\nShutting down... Goodbye!")
            break

if __name__ == "__main__":
    main_menu()