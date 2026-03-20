# --- PMTool: PROCUREMENT MODULE ---
import storage
import settings

def manage_suppliers(config):
    """Handles adding and viewing the global supplier list."""
    while True:
        print("\n--- SUPPLIER LIST ---")
        suppliers = config.get('suppliers', [])
        for i, sup in enumerate(suppliers):
            print(f"{i+1}. {sup}")
        
        print("\nN. Add New Supplier")
        print("0. Back")
        
        choice = input("Select: ").strip().upper()
        if choice == '0':
            break
        elif choice == 'N':
            new_sup = input("Enter new supplier name: ").strip()
            if new_sup:
                config.setdefault('suppliers', []).append(new_sup)
                settings.save_settings(config)
                print(f">> {new_sup} added to suppliers.")

def assign_supplier_and_tag(mats, index, config):
    """Tags an item as Ready to Order and assigns a supplier."""
    suppliers = config.get('suppliers', [])
    print("\n--- SELECT SUPPLIER ---")
    for i, sup in enumerate(suppliers):
         print(f"{i+1}. {sup}")
    print("0. Leave as TBA")
    
    sup_choice = input("Select Supplier #: ").strip()
    supplier_name = "TBA"
    if sup_choice.isdigit() and 0 < int(sup_choice) <= len(suppliers):
        supplier_name = suppliers[int(sup_choice)-1]
        
    mats[index]['supplier'] = supplier_name
    mats[index]['procurement_status'] = 'Ready to Order'
    print(f">> Tagged as 'Ready to Order' with supplier: {supplier_name}")

def project_procurement_dashboard(selected_project, index, config):
    """Project-specific materials tracking and tagging."""
    while True:
        print(f"\n--- PROCUREMENT: {selected_project['Project']} ---")
        mats = selected_project.get('Materials', [])
        
        if not mats:
            print("No materials listed for this project.")
        
        # Display current materials and their statuses
        for i, m in enumerate(mats):
            status = m.get('procurement_status', 'Pending')
            supplier = m.get('supplier', 'TBA')
            print(f"{i+1}. [{status.upper()}] {m['name']} (Supplier: {supplier} | Est: ${m.get('estimated_cost', 0):.2f})")
            
        print("\nActions:")
        print("T. Tag item as 'Ready to Order'")
        print("R. Mark item as 'Received' (Arrived)")
        print("A. Add extra material to project")
        print("0. Back")
        
        choice = input("Select action: ").strip().upper()
        
        if choice == '0':
            break
            
        elif choice == 'T':
            item_num = input("Enter material # to tag: ").strip()
            if item_num.isdigit() and 0 < int(item_num) <= len(mats):
                assign_supplier_and_tag(mats, int(item_num)-1, config)
                storage.update_project(index, selected_project)
            else:
                print("!! Invalid selection.")
                
        elif choice == 'R':
            item_num = input("Enter material # that has arrived: ").strip()
            if item_num.isdigit() and 0 < int(item_num) <= len(mats):
                mats[int(item_num)-1]['procurement_status'] = 'Received'
                storage.update_project(index, selected_project)
                print(">> Item marked as Received in inventory.")
            else:
                print("!! Invalid selection.")
                
        elif choice == 'A':
            # Simple addition for procurement needs
            name = input("Material Name: ").strip()
            try:
                est_cost = float(input("Estimated Cost ($): "))
                mats.append({
                    "name": name, 
                    "estimated_cost": est_cost, 
                    "actual_cost": 0.0, 
                    "procurement_status": "Pending",
                    "supplier": "TBA",
                    "markup_percent": config.get('markup_rate', 0.15) * 100
                })
                storage.update_project(index, selected_project)
                print(">> Extra material added to project.")
            except ValueError:
                print("!! Invalid cost.")

def select_active_project_ui(config):
    """Helper to pick a project for procurement."""
    logs = storage.get_all_history()
    active_projects = [(i, p) for i, p in enumerate(logs) if p.get('Status') == 'Active']
    
    if not active_projects:
        print("\n!! No 'Active' projects found. Change a project's status to Active first.")
        input("Press Enter to return...")
        return
        
    print("\n--- SELECT ACTIVE PROJECT ---")
    for display_idx, (real_idx, p) in enumerate(active_projects):
        print(f"{display_idx+1}. {p.get('Project_ID')} - {p['Project']}")
        
    choice = input("\nSelect Project # (0 to cancel): ")
    if choice.isdigit() and 0 < int(choice) <= len(active_projects):
        real_idx, selected_project = active_projects[int(choice)-1]
        project_procurement_dashboard(selected_project, real_idx, config)

def view_ready_to_order_list():
    """Global view of all tagged items waiting for Purchase Orders."""
    print("\n" + "="*80)
    print("   MASTER 'READY TO ORDER' LIST (PRE-PO STAGING)   ")
    print("="*80)
    
    logs = storage.get_all_history()
    items_found = False
    
    # We can group by Supplier for easier PO creation later
    print(f"{'Job No':<10} | {'Supplier':<20} | {'Material':<35} | {'Est Cost'}")
    print("-" * 80)
    
    for project in logs:
        # Only look at Active projects
        if project.get('Status') != 'Active':
            continue
            
        mats = project.get('Materials', [])
        for m in mats:
            if m.get('procurement_status') == 'Ready to Order':
                items_found = True
                job_no = project.get('Project_ID', 'N/A')
                sup = m.get('supplier', 'TBA')[:18]
                name = m.get('name', 'Unknown')[:33]
                cost = m.get('estimated_cost', 0)
                print(f"{job_no:<10} | {sup:<20} | {name:<35} | ${cost:,.2f}")
                
    if not items_found:
        print("No items currently tagged as 'Ready to Order'.")
        
    print("-" * 80)
    # Placeholder for future PO generation logic
    print("NOTE: Automated PO Generation will be attached to this list in a future update.")
    input("\nPress Enter to return...")

def procurement_main_menu():
    """Main routing menu for the Procurement module."""
    while True:
        config = settings.load_settings()
        print("\n" + "="*40)
        print("   PMTool: PROCUREMENT   ")
        print("="*40)
        print("1. Project Materials (Tag & Receive)")
        print("2. 'Ready to Order' Master List")
        print("3. Manage Supplier Database")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect: ").strip()
        
        if choice == '1':
            select_active_project_ui(config)
        elif choice == '2':
            view_ready_to_order_list()
        elif choice == '3':
            manage_suppliers(config)
        elif choice == '0':
            break