import engine
import storage
import labour
import materials
import reports
import status
import metadata
import notes
import settings
import procurement
import po_generator
import tutorial
import os
import database
import estimate

def view_history_menu(filter_status=None):
    show_mode = "Filtered" if filter_status else "All Live" 
    search_results = []

    while True:
        logs = storage.get_all_history()
        
        is_estimating = filter_status and ("Draft" in filter_status or "Quoted" in filter_status)
        
        print("\n" + "-"*85)
        header_title = "ESTIMATES" if is_estimating else "PROJECTS"
        print(f"{'ID (Job/Quote)':<15} | {header_title:<25} | {'Total (Inc)':<14} | {'Status'}")
        print("-" * 85)

        if not logs:
            print("No records found in database.")
        else:
            if filter_status:
                display_list = [log for log in logs if log.get("Status") in filter_status]
            elif show_mode == "All Live":
                display_list = [log for log in logs if log.get("Status") != "Archived"]
            elif show_mode == "Search":
                display_list = search_results
            else: # show_mode == "Everything"
                display_list = logs

            if not display_list:
                print(f"No {header_title.lower()} currently match this view.")
            else:
                for entry in display_list:
                    display_id = entry.get('Project_ID') if entry.get('Project_ID') else entry.get('Quote_Number', 'N/A')
                    status_label = f"[{entry.get('Status', 'Draft').upper()}]"
                    print(f"{display_id:<15} | {entry['Project'][:25]:<25} | ${entry.get('Total_Inc_GST', 0):<13,.2f} | {status_label}")
        
        print("-" * 85)

        if is_estimating:
            choice = input("Enter ID, 'N' for New Estimate, 'S' for Search, 'F' to Filter, or '0' to exit: ").strip().upper()
        else:
            choice = input("Enter ID, 'S' for Search, 'F' to Filter, or '0' to exit: ").strip().upper()
        
        if choice == '0': 
            break
        elif choice == 'N' and is_estimating:
            estimate.create_estimate()
        elif choice == 'F':
            print("\n--- FILTER BY STATUS ---")
            print("1. All Live (Excludes Archived)")
            print("2. Draft")
            print("3. Quoted")
            print("4. Active")
            print("5. Completed")
            print("6. Invoiced")
            print("7. Archived")
            print("8. Show Absolutely Everything")
            
            f_choice = input("Select View # (0 to cancel): ")
            filter_map = {"2": ["Draft"], "3": ["Quoted"], "4": ["Active"], "5": ["Completed"], "6": ["Invoiced"], "7": ["Archived"]}
            
            if f_choice == '1':
                filter_status = None
                show_mode = "All Live"
            elif f_choice in filter_map:
                filter_status = filter_map[f_choice]
                show_mode = "Filtered"
            elif f_choice == '8':
                filter_status = None
                show_mode = "Everything"
            continue
        elif choice == 'S':
            term = input("Enter search term: ").strip().lower()
            search_results = [
                log for log in logs 
                if term in log.get('Project', '').lower() 
                or term in log.get('Project_ID', '').lower()
                or term in log.get('Quote_Number', '').lower()
            ]
            show_mode = "Search"
            continue
        elif choice != '0' and choice != 'N':
            selected = None
            idx = -1
            
            config = settings.load_settings()
            job_prefix = config.get('id_prefix', 'JN-')
            quote_prefix = config.get('quote_prefix', 'QT-')
            
            search_terms = [choice]
            if choice.isdigit():
                search_terms.append(f"{job_prefix}{choice}")
                search_terms.append(f"{quote_prefix}{choice}")

            for i, entry in enumerate(logs):
                if entry.get('Project_ID') in search_terms or entry.get('Quote_Number') in search_terms:
                    selected = entry
                    idx = i
                    break
            
            if selected:
                project_submenu(selected, idx)
            else:
                print("!! Job/Quote ID not found.")

def main_menu():
    while True:
        print("\n" + "="*40)
        print("   PMTool: MAIN MENU   ")
        print("="*40)
        print("1. ESTIMATING (New & Draft Quotes)")
        print("2. ACTIVE PROJECTS (Manage Live Jobs)")
        print("3. PROJECT HISTORY (Completed, Invoiced, Archived)") # <-- NEW OPTION
        print("4. PROCUREMENT")
        print("5. SETTINGS")
        print("6. EXIT")
        
        choice = input("\nSelect: ").strip()
        
        if choice == '1': 
            view_history_menu(filter_status=["Draft", "Quoted"])
        elif choice == '2': 
            view_history_menu(filter_status=["Active"])
        elif choice == '3': 
            view_history_menu(filter_status=["Completed", "Invoiced", "Archived"])
        elif choice == '4':
            procurement.procurement_main_menu()
        elif choice == '5': 
            settings.settings_menu_ui() 
        elif choice == '6':
            print("\nShutting down... Goodbye!")
            break

def project_submenu(selected, idx):
    """The detailed view for an individual project or estimate."""
    while True:
        logs = storage.get_all_history()
        selected = logs[idx]
        reports.print_project_dashboard(selected)
        
        print(f"\nSTATUS: {selected.get('Status', 'Draft').upper()}")
        
        # 1. Is it dead? (Archived)
        is_archived = selected.get('Status') == 'Archived'
        
        # 2. Is it an estimate? (True if it lacks a Job Number)
        is_estimate = not selected.get('Project_ID') 
        
        # Render the correct menu
        if is_archived:
            print("\n*** ARCHIVED (READ-ONLY) ***")
            print("1. Restore (Change Status) | 2. Back")
        elif is_estimate:
            print("1. Change Status (e.g., Accept Quote) | 2. Back | 3. Edit Estimate Labor | 4. Edit Estimate Materials")
        else:
            print("1. Change Status | 2. Back | 3. Log Actual Labor | 4. Log Material Costs | 5. Add Note")
        
        action = input("Choice: ")
        
        # Handle the routing
        if is_archived:
            if action == '1':
                status.change_status_ui(selected, idx)
            elif action == '2':
                break
                
        elif is_estimate:
            if action == '1':
                status.change_status_ui(selected, idx)
            elif action == '2':
                break
            elif action == '3':
                labour.log_hours_ui(selected, idx)
            elif action == '4':
                materials.log_materials_ui(selected, idx)
                
        else: # Active Project
            if action == '1':
                status.change_status_ui(selected, idx)
            elif action == '2':
                break
            elif action == '3':
                labour.log_hours_ui(selected, idx)
            elif action == '4':
                materials.log_materials_ui(selected, idx)
            elif action == '5':
                notes.add_note_ui(selected, idx)

def startup_check():
    """Checks if config.json exists. If not, triggers the onboarding wizard."""
    if not os.path.exists(settings.CONFIG_FILE):
        print("\n" + "*"*60)
        print("   WELCOME TO BASELINE - PROJECT MANAGEMENT TOOL   ")
        print("*"*60)
        
        demo = input("\nWould you like to view a quick tutorial? (Y/N): ").strip().upper()
        if demo == 'Y':
            tutorial.run_demo()
        
        settings.run_first_time_setup()
        input("\nPress Enter to open the Main Menu...")

if __name__ == "__main__":
    startup_check()
    main_menu()