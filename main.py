import engine
import storage
import labour
import materials
import reports
import status
import metadata
import notes
import settings

def create_estimate():
    name = input("Project Name: ")
    scope = input("Scope: ")
    meta = metadata.get_project_metadata() 
    
    # 1. Get labor first
    labor = labour.get_labour_inputs()
    # 2. Pass labor INTO materials so assemblies can append to it!
    mats = materials.get_material_inputs(labor) 
    
    base = engine.calculate_totals(labor, mats)
    tax = engine.calculate_gst(base['total_ex'])
    
    storage.save_to_db(name, scope, meta['client'], meta['target_date'], labor, mats, base['total_ex'], tax['gst_value'], tax['total_inc_gst'])
    
    logs = storage.get_all_history()
    logs[-1]["Status"] = "Draft"
    storage.overwrite_db(logs)
    
    print("\n>> Saved as Draft.")

def view_history_menu():
    show_mode = "All Live" 
    search_results = []

    while True:
        logs = storage.get_all_history()
        if not logs:
            print("\nNo records found.")
            input("Press Enter to return...")
            break
        
        print("\n" + "-"*80)
        header_title = f"{show_mode.upper()} PROJECTS"
        print(f"{'Job No.':<10} | {header_title:<25} | {'Total (Inc)':<14} | {'Lifecycle Phase'}")
        print("-" * 80)

        # --- DYNAMIC FILTERING ---
        if show_mode == "All Live":
            display_list = [log for log in logs if log.get("Status", "Active") != "Archived"]
        elif show_mode == "Search":
            display_list = search_results
        else:
            display_list = [log for log in logs if log.get("Status", "Active").title() == show_mode]

        for entry in display_list:
            jid = entry.get('Project_ID', 'N/A')
            status_label = f"[{entry.get('Status', 'Active').upper()}]"
            print(f"{jid:<10} | {entry['Project'][:25]:<25} | ${entry.get('Total_Inc_GST', 0):<13,.2f} | {status_label}")
        print("-" * 80)

        choice = input("Enter Job No, 'F' to Filter, 'S' to Search, or '0' to exit: ").strip().upper()
        
        if choice == '0': 
            break
            
        elif choice == 'F':
            print("\n--- FILTER BY STATUS ---")
            print("1. All Live (Excludes Archived)")
            print("2. Draft")
            print("3. Quoted")
            print("4. Active")
            print("5. Completed")
            print("6. Invoiced")
            print("7. Archived")
            
            f_choice = input("Select View # (0 to cancel): ")
            filter_map = {"1": "All Live", "2": "Draft", "3": "Quoted", "4": "Active", "5": "Completed", "6": "Invoiced", "7": "Archived"}
            
            if f_choice in filter_map:
                show_mode = filter_map[f_choice]
            continue
                
        elif choice == 'S':
            term = input("Enter search term: ").strip().lower()
            search_results = [log for log in logs if term in log.get('Project', '').lower() or term in log.get('Project_ID', '').lower()]
            show_mode = "Search"
            continue
            
        else:
            # --- UPDATED: Dynamic Prefix Search ---
            config = settings.load_settings()
            prefix = config['id_prefix']
            search_id = f"{prefix}{choice}" if (not choice.startswith(prefix) and choice.isdigit()) else choice
            
            selected = None
            idx = -1
            
            for i, entry in enumerate(logs):
                if entry.get('Project_ID') == search_id:
                    selected = entry
                    idx = i
                    break
                    
            if selected:
                # --- NEW: STICKY PROJECT LOOP ---
                while True:
                    # Fetch fresh data every loop in case it was updated
                    logs = storage.get_all_history()
                    selected = logs[idx]
                    
                    reports.print_project_dashboard(selected)
                    
                    is_archived = selected.get('Status', 'Active') == 'Archived'
                    
                    if is_archived:
                        print("\n*** PROJECT IS ARCHIVED (READ-ONLY) ***")
                        print("1. Restore (Change Status) | 2. Back")
                        action = input("Choice: ")
                        if action == '1':
                            status.change_status_ui(selected, idx)
                        elif action == '2':
                            break # Exits the project and goes back to the list
                    else:
                        print(f"\nSTATUS: {selected.get('Status', 'Active').upper()}")
                        # UPDATED MENU: Added Option 5
                        print("1. Change Status | 2. Back | 3. Log Labor | 4. Log Material Costs | 5. Add Note")
                        action = input("Choice: ")
                        
                        if action == '1':
                            status.change_status_ui(selected, idx)
                        elif action == '2':
                            break # Exits the project and goes back to the list
                        elif action == '3':
                            labour.log_hours_ui(selected, idx)
                        elif action == '4':
                            materials.log_materials_ui(selected, idx)
                        elif action == '5':
                            notes.add_note_ui(selected, idx)
            else:
                print("!! Job Number not found. Please try again.")

def main_menu():
    while True:
        print("\n" + "="*40)
        print("   PMTool: MAIN MENU   ")
        print("="*40)
        print("1. Create New Estimate")
        print("2. Manage History")
        print("3. Global Settings") 
        print("4. EXIT")            
        
        choice = input("\nSelect: ")
        
        if choice == '1': 
            create_estimate()
        elif choice == '2': 
            view_history_menu()
        elif choice == '3': 
            settings.settings_menu_ui() 
        elif choice == '4':
            print("\nShutting down... Goodbye!")
            break

if __name__ == "__main__":
    main_menu()