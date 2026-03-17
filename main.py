import engine
import storage
import labour  
import materials # NEW: Importing the materials module

def create_estimate():
    name = input("Project Name: ")
    scope = input("Scope: ")
    # Using the modular inputs
    labor = labour.get_labour_inputs()
    mats = materials.get_material_inputs()
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
        
        # --- PROJECT LIST ---
        print("\n" + "-"*55)
        print(f"{'Job No.':<10} | {'Project Name':<25} | {'Total (Inc)'}")
        print("-"*55)
        
        for entry in logs:
            # Safely handle older projects that don't have an ID yet
            jid = entry.get('Project_ID', 'N/A')
            total_inc = entry.get('Total_Inc_GST', 0)
            print(f"{jid:<10} | {entry['Project']:<25} | ${total_inc:,.2f}")
        
        print("-"*55)

        # --- SELECTION & SEARCH LOGIC ---
        choice = input("Enter Job No (e.g., 1000), 'S' to Search, or '0' to exit: ").strip().upper()
        
        if choice == '0': 
            break
            
        elif choice == 'S':
            term = input("Enter search term (Name or Job No): ").strip().lower()
            print("\n--- SEARCH RESULTS ---")
            results = [log for log in logs if term in log.get('Project', '').lower() or term in log.get('Project_ID', '').lower()]
            
            if results:
                for entry in results:
                    jid = entry.get('Project_ID', 'N/A')
                    print(f"{jid:<10} | {entry['Project']:<25} | ${entry.get('Total_Inc_GST', 0):,.2f}")
            else:
                print("!! No matches found.")
            input("\nPress Enter to return to list...")
            continue # Loop back to the top of the menu
            
        else:
            # --- VIEW DETAILS LOGIC ---
            # Forgiving input: Allows user to type "1000" instead of "JN-1000"
            if not choice.startswith("JN-") and choice.isdigit():
                search_id = f"JN-{choice}"
            else:
                search_id = choice
                
            # Find the specific project and its actual list index
            selected = None
            idx = -1
            for i, entry in enumerate(logs):
                if entry.get('Project_ID') == search_id:
                    selected = entry
                    idx = i
                    break
                    
            if selected:
                print("\n" + "="*75)
                print(f"JOB NO:  {selected.get('Project_ID', 'N/A')}")
                print(f"PROJECT: {selected['Project'].upper()} | DATE: {selected.get('Timestamp', 'N/A')}")
                print(f"SCOPE:   {selected.get('Scope', 'N/A')}")
                print("-" * 75)
                
                # --- DETAILED LABOR TRACKER ---
                print(f"{'Role':<12} | {'Orig Hr':>7} | {'Used':>5} | {'Rem Hr':>6} | {'Rem $':>12} | {'Var $':>10}")
                print("-" * 75)
                
                labor_data = selected.get('Labor', [])
                total_orig_lab_val = 0
                total_rem_lab_val = 0
                total_var_lab_val = 0

                for l in labor_data:
                    orig = l.get('estimated_hours', l.get('hours', 0))
                    used = l.get('actual_hours', 0)
                    rate = l.get('rate', 0)
                    
                    rem_hrs = orig - used
                    rem_cost = max(0, rem_hrs * rate)
                    var_cost = (used - orig) * rate if used > orig else 0.0
                    
                    total_orig_lab_val += (orig * rate)
                    total_rem_lab_val += rem_cost
                    total_var_lab_val += var_cost

                    print(f"{l['role']:<12} | {orig:>7.1f} | {used:>5.1f} | {rem_hrs:>6.1f} | ${rem_cost:>11,.2f} | ${var_cost:>9,.2f}")
                
                print("-" * 75)
                print(f"{'LABOR TOTALS':<12} | {'':>7} | {'':>5} | {'':>6} | ${total_rem_lab_val:>11,.2f} | ${total_var_lab_val:>9,.2f}")
                
                # --- DETAILED MATERIALS TRACKER ---
                print("\n" + f"{'Material Item':<27} | {'Orig $':>10} | {'Spent $':>10} | {'Rem $':>10} | {'Var $':>9}")
                print("-" * 75)
                
                mats_data = selected.get('Materials', [])
                total_orig_mat_val = 0
                total_rem_mat_val = 0
                total_var_mat_val = 0
                
                for m in mats_data:
                    # Safely handle old 'price' key and new 'estimated_cost' key
                    orig_cost = m.get('estimated_cost', m.get('price', 0))
                    spent = m.get('actual_cost', 0)
                    
                    rem_cost = max(0, orig_cost - spent)
                    var_cost = (spent - orig_cost) if spent > orig_cost else 0.0
                    
                    total_orig_mat_val += orig_cost
                    total_rem_mat_val += rem_cost
                    total_var_mat_val += var_cost
                    
                    print(f"{m['name']:<27} | ${orig_cost:>8,.2f} | ${spent:>8,.2f} | ${rem_cost:>8,.2f} | ${var_cost:>8,.2f}")
                
                print("-" * 75)
                print(f"{'MAT TOTALS':<27} | {'':>10} | {'':>10} | ${total_rem_mat_val:>8,.2f} | ${total_var_mat_val:>8,.2f}")

                # --- GRAND SUMMARY ---
                print("=" * 75)
                total_orig_budget = total_orig_lab_val + total_orig_mat_val
                total_variance = total_var_lab_val + total_var_mat_val
                
                print(f"{'Original Base Budget (Lab + Mat):':<58} | ${total_orig_budget:>11,.2f}")
                if total_variance > 0:
                    print(f"{'TOTAL OVERRUN (LOSS):':<58} | ${total_variance:>11,.2f}")
                print("-" * 75)
                print(f"{'GRAND TOTAL (Inc GST & Contingency):':<58} | ${selected.get('Total_Inc_GST', 0):11,.2f}")
                print("=" * 75)
                
                print("\n1. Delete | 2. Back | 3. Log Labor | 4. Log Material Costs")
                action = input("Choice: ")
                if action == '1':
                    if input("Confirm Delete? (y/n): ").lower() == 'y':
                        storage.delete_project_by_index(idx)
                        # Break not needed; while loop will refresh the list
                elif action == '3':
                    log_hours_ui(selected, idx)
                elif action == '4':
                    log_materials_ui(selected, idx)
            else:
                print("!! Job Number not found. Please try again.")

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