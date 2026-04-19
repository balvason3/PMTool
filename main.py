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
import estimate_generator
import tutorial
import os
import estimate
import auth
import getpass
import variation

# --- GLOBAL SESSION STATE ---
current_user = None
current_role = None

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
            choice = input("Enter ID, 'N' for New Estimate, 'G' for Generate PDF, 'S' for Search, 'F' to Filter, or '0' to exit: ").strip().upper()
        else:
            choice = input("Enter ID, 'S' for Search, 'F' to Filter, or '0' to exit: ").strip().upper()
        
        if choice == '0': 
            break
        elif choice == 'N' and is_estimating:
            estimate.create_estimate()
        elif choice == 'G' and is_estimating:
            estimate_generator.generate_estimate_pdf_ui()
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
                project_submenu(selected, idx, config)
            else:
                print("!! Job/Quote ID not found.")

def project_submenu(selected, idx, config=None):
    """The detailed view for an individual project or estimate."""
    if config is None:
        config = settings.load_settings()
    
    while True:
        logs = storage.get_all_history()
        selected = logs[idx]
        reports.print_project_dashboard(selected)
        
        print(f"\nSTATUS: {selected.get('Status', 'Draft').upper()}")
        
        is_archived = selected.get('Status') == 'Archived'
        is_estimate = not selected.get('Project_ID') 
        
        if is_archived:
            print("\n*** ARCHIVED (READ-ONLY) ***")
            print("1. Restore (Change Status) | 2. Back")
        elif is_estimate:
            print("1. Change Status (e.g., Accept Quote) | 2. Back | 3. Edit Estimate Labor | 4. Edit Estimate Materials | 5. Generate PDF")
        else:
            print("1. Change Status | 2. Back | 3. Log Actual Labor | 4. Log Material Costs | 5. Add Note | 6. Variation")
        
        action = input("Choice: ")
        
        if is_archived:
            if action == '1': status.change_status_ui(selected, idx)
            elif action == '2': break
                
        elif is_estimate:
            if action == '1': status.change_status_ui(selected, idx)
            elif action == '2': break
            elif action == '3': labour.log_hours_ui(selected, idx, config)
            elif action == '4': materials.log_materials_ui(selected, idx, config)
            elif action == '5': estimate_generator.generate_estimate_pdf_ui()
                
        else: # Active Project
            if action == '1': status.change_status_ui(selected, idx)
            elif action == '2': break
            elif action == '3': labour.log_hours_ui(selected, idx, config)
            elif action == '4': materials.log_materials_ui(selected, idx, config)
            elif action == '5': notes.add_note_ui(selected, idx)
            elif action == '6': variation.variations_menu(selected, current_user)

def first_boot_setup():
    """Forces the creation of the Master Admin account on a fresh database."""
    print("\n" + "*"*60)
    print("   SECURITY INITIALIZATION: MASTER ADMIN SETUP   ")
    print("*"*60)
    print("Welcome to Bedrock! Before we begin, you must create a Master Admin account.\n")
    
    while True:
        admin_user = input("Choose an Admin Username: ").strip()
        if not admin_user:
            continue
            
        admin_pass = getpass.getpass("Choose a Secure Password: ")
        admin_pass2 = getpass.getpass("Confirm Password: ")
        
        if admin_pass != admin_pass2:
            print("!! Passwords do not match. Please try again.\n")
            continue
            
        if len(admin_pass) < 4:
            print("!! Password must be at least 4 characters long.\n")
            continue
            
        success, msg = auth.create_user(admin_user, admin_pass, "Admin")
        if success:
            print(msg)
            print(">> Master Admin account created successfully! Please log in.")
            break
        else:
            print(msg)

def login_screen():
    """The security barrier. Users must pass this to reach the Main Menu."""
    print("\n" + "="*40)
    print("         BEDROCK: SECURE LOGIN         ")
    print("="*40)
    
    while True:
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        
        success, role = auth.authenticate_user(username, password)
        
        if success:
            print(f"\n>> Authentication Successful. Welcome back, {username}! (Role: {role})")
            return username, role
        else:
            print("!! Invalid Username or Password. Please try again.\n")

def main_menu():
    global current_user, current_role
    while True:
        print("\n" + "="*40)
        print("   BEDROCK: MAIN MENU   ")
        print("="*40)
        print(f"Logged in as: {current_user} [{current_role}]")
        print("-" * 40)
        print("1. ESTIMATING (New & Draft Quotes)")
        print("2. ACTIVE PROJECTS (Manage Live Jobs)")
        print("3. PROJECT HISTORY (Completed, Invoiced, Archived)") 
        print("4. PROCUREMENT")
        print("5. SETTINGS")
        print("6. LOGOUT / EXIT")
        
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
            print("\nLogging out... Goodbye!")
            break

def startup_check():
    global current_user, current_role
    
    # 1. Security Engine Initialization
    auth.initialize_roles()
    
    if auth.check_first_boot():
        print("\n" + "*"*60)
        print("   WELCOME TO BEDROCK - PROJECT MANAGEMENT TOOL   ")
        print("*"*60)
        demo = input("\nWould you like to view a quick tutorial? (Y/N): ").strip().upper()
        if demo == 'Y':
            tutorial.run_demo()
        first_boot_setup()
        
    # 2. Present the Login Barrier
    current_user, current_role = login_screen()

if __name__ == "__main__":
    startup_check()
    main_menu()