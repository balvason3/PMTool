import engine
import storage
import labour  
import materials 
import reports 

def create_estimate():
    name = input("Project Name: ")
    scope = input("Scope: ")
    labor = labour.get_labour_inputs()
    mats = materials.get_material_inputs()
    base = engine.calculate_totals(labor, mats)
    tax = engine.calculate_gst(base['total_ex'])
    storage.save_to_db(name, scope, labor, mats, base['total_ex'], tax['gst_value'], tax['total_inc_gst'])
    print("\n>> Saved.")

def view_history_menu():
    show_mode = "Active" # Tracks which 'tab' we are looking at
    search_results = []

    while True:
        logs = storage.get_all_history()
        if not logs:
            print("\nNo records found.")
            input("Press Enter to return...")
            break
        
        # --- DYNAMIC LIST HEADER ---
        print("\n" + "-"*65)
        if show_mode == "Active":
            print(f"{'Job No.':<10} | {'ACTIVE PROJECTS':<25} | {'Total (Inc)':<15} | {'Status'}")
        elif show_mode == "Archived":
            print(f"{'Job No.':<10} | {'ARCHIVED PROJECTS':<25} | {'Total (Inc)':<15} | {'Status'}")
        else:
            print(f"{'Job No.':<10} | {'SEARCH RESULTS':<25} | {'Total (Inc)':<15} | {'Status'}")
        print("-" * 65)

        # --- FILTER THE LIST ---
        if show_mode == "Active":
            display_list = [log for log in logs if log.get("Status", "Active") == "Active"]
        elif show_mode == "Archived":
            display_list = [log for log in logs if log.get("Status", "Active") == "Archived"]
        elif show_mode == "Search":
            display_list = search_results

        # --- PRINT THE LIST ---
        for entry in display_list:
            jid = entry.get('Project_ID', 'N/A')
            print(f"{jid:<10} | {entry['Project'][:25]:<25} | ${entry.get('Total_Inc_GST', 0):<14,.2f} | {entry.get('Status', 'Active')}")
        print("-" * 65)

        # --- DYNAMIC PROMPT ---
        if show_mode == "Active":
            choice = input("Enter Job No, 'S' for Search, 'A' for Archives, or '0' to exit: ").strip().upper()
        else:
            choice = input("Enter Job No to view, or '0' to return to Active list: ").strip().upper()
        
        # --- HANDLE NAVIGATION ---
        if choice == '0': 
            if show_mode != "Active":
                show_mode = "Active" # Go back to main tab
                continue
            else:
                break # Exit history menu completely
                
        elif choice == 'S' and show_mode == "Active":
            term = input("Enter search term: ").strip().lower()
            search_results = [log for log in logs if term in log.get('Project', '').lower() or term in log.get('Project_ID', '').lower()]
            show_mode = "Search"
            continue
            
        elif choice == 'A' and show_mode == "Active":
            show_mode = "Archived"
            continue
            
        else:
            # --- VIEW SELECTED PROJECT ---
            search_id = f"JN-{choice}" if (not choice.startswith("JN-") and choice.isdigit()) else choice
            selected = None
            idx = -1
            
            # Find the true index in the main logs list
            for i, entry in enumerate(logs):
                if entry.get('Project_ID') == search_id:
                    selected = entry
                    idx = i
                    break
                    
            if selected:
                # 1. Print the Dashboard
                reports.print_project_dashboard(selected)
                
                # 2. Check the Status for Read-Only Lock
                is_archived = selected.get('Status', 'Active') == 'Archived'
                
                if is_archived:
                    print("\n*** PROJECT IS ARCHIVED (READ-ONLY) ***")
                    print("1. Restore (Unarchive) | 2. Back")
                    action = input("Choice: ")
                    if action == '1':
                        if input("Restore project to Active? (y/n): ").lower() == 'y':
                            storage.restore_project_by_index(idx)
                            print(">> Project Restored.")
                            show_mode = "Active" # Kick them back to the active list to see it
                else:
                    print(f"\nSTATUS: {selected.get('Status', 'Active').upper()}")
                    print("1. Archive Project | 2. Back | 3. Log Labor | 4. Log Material Costs")
                    action = input("Choice: ")
                    
                    if action == '1':
                        if input("Confirm Archive? (y/n): ").lower() == 'y':
                            storage.archive_project_by_index(idx)
                            print(">> Project Archived.")
                    elif action == '3':
                        labour.log_hours_ui(selected, idx)
                    elif action == '4':
                        materials.log_materials_ui(selected, idx)
            else:
                print("!! Job Number not found. Please try again.")

def main_menu():
    while True:
        print("\n" + "="*40)
        print("   PMTool: MAIN MENU (Modular)   ")
        print("="*40)
        print("1. Create New Estimate")
        print("2. Manage History")
        print("3. EXIT")
        choice = input("\nSelect: ")
        if choice == '1': create_estimate()
        elif choice == '2': view_history_menu()
        elif choice == '3':
            print("\nShutting down... Goodbye!")
            break

if __name__ == "__main__":
    main_menu()