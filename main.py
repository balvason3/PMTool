import engine
import storage
import labour  
import materials 
import reports # Import our new display module

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
    while True:
        logs = storage.get_all_history()
        if not logs:
            print("\nNo records found.")
            input("Press Enter to return...")
            break
        
        print("\n" + "-"*55)
        print(f"{'Job No.':<10} | {'Project Name':<25} | {'Total (Inc)'}")
        print("-"*55)
        for entry in logs:
            jid = entry.get('Project_ID', 'N/A')
            print(f"{jid:<10} | {entry['Project']:<25} | ${entry.get('Total_Inc_GST', 0):,.2f}")
        print("-"*55)

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
            continue
            
        else:
            search_id = f"JN-{choice}" if (not choice.startswith("JN-") and choice.isdigit()) else choice
            selected = None
            idx = -1
            for i, entry in enumerate(logs):
                if entry.get('Project_ID') == search_id:
                    selected = entry
                    idx = i
                    break
                    
            if selected:
                # 1. CALL THE REPORT DISPLAY
                reports.print_project_dashboard(selected)
                
                # 2. HANDLE THE SUB-MENU ROUTING
                print("\n1. Delete | 2. Back | 3. Log Labor | 4. Log Material Costs")
                action = input("Choice: ")
                if action == '1':
                    if input("Confirm Delete? (y/n): ").lower() == 'y':
                        storage.delete_project_by_index(idx)
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