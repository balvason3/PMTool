# --- PMTool: GLOBAL SETTINGS MODULE ---
import json
import os

DATA_DIR = 'data'
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

DEFAULT_SETTINGS = {
    "gst_rate": 0.10,
    "markup_rate": 0.15, 
    "id_prefix": "JN-",
    "start_number": 10000,
    "company_details": {
        "name": "YOUR COMPANY NAME",
        "abn": "XX XXX XXX XXX",
        "address": "123 Business Street",
        "phone": "0400 000 000",
        "email": "admin@yourcompany.com.au"
    },
    "standard_roles": [
        {"name": "Project Manager", "rate": 120.0},
        {"name": "Site Supervisor", "rate": 90.0},
        {"name": "Admin", "rate": 50.0},
        {"name": "Electrician", "rate": 85.0},
        {"name": "Plumber", "rate": 85.0},
        {"name": "Carpenter", "rate": 75.0},
        {"name": "General Labor", "rate": 50.0}
    ],
    # NEW: Standard Materials & Assemblies Database
    "standard_materials": [
        {"name": "Standard Power Point", "cost": 15.00, "is_assembly": False},
        {"name": "LED Downlight", "cost": 25.00, "is_assembly": False},
        {
            "name": "Rough-In Electrical Wire (per m)", 
            "cost": 2.50, 
            "is_assembly": True,
            "consumables_cost": 0.20,
            "labor_role": "Electrician",
            "labor_hours": 0.05
        }
    ]
}

def load_settings():
    os.makedirs(DATA_DIR, exist_ok=True) # <-- ADD THIS LINE
    if not os.path.exists(CONFIG_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        needs_save = False
        
        if 'contingency_rate' in config and 'markup_rate' not in config:
            config['markup_rate'] = config.pop('contingency_rate')
            needs_save = True
            
        if 'standard_roles' not in config:
            config['standard_roles'] = DEFAULT_SETTINGS['standard_roles']
            needs_save = True
        elif config['standard_roles'] and isinstance(config['standard_roles'][0], str):
            config['standard_roles'] = [{"name": r, "rate": 0.0} for r in config['standard_roles']]
            needs_save = True
            
        # Inject standard materials if missing
        if 'standard_materials' not in config:
            config['standard_materials'] = DEFAULT_SETTINGS['standard_materials']
            needs_save = True
            
        if needs_save:
            save_settings(config)
            
        return config

def save_settings(settings):
    os.makedirs(DATA_DIR, exist_ok=True) # <-- ADD THIS LINE
    with open(CONFIG_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def procurement_main_menu():
    """Main routing menu for the Procurement module."""
    while True:
        config = settings.load_settings()
        print("\n" + "="*40)
        print("   PMTool: PROCUREMENT   ")
        print("="*40)
        print("1. Project Materials (Tag & Receive)")
        print("2. 'Ready to Order' Master List")
        print("3. Generate Purchase Order")   
        print("4. Manage Supplier Database")  
        print("0. Back to Main Menu")
        
        choice = input("\nSelect: ").strip()
        
        if choice == '1':
            select_active_project_ui(config)
        elif choice == '2':
            view_ready_to_order_list()
        elif choice == '3':
            po_generator.generate_purchase_order_ui()  # <-- CALLS THE NEW FILE
        elif choice == '4':
            supplier.supplier_menu_ui()
        elif choice == '0':
            break
        else:
            print("!! Invalid choice.")

def settings_menu_ui():
    """Main settings dashboard."""
    while True:
        config = load_settings()
        
        # Inject standard materials if missing
        if 'standard_materials' not in config:
            config['standard_materials'] = DEFAULT_SETTINGS['standard_materials']
            save_settings(config)
            
        # Inject company details if missing
        if 'company_details' not in config:
            config['company_details'] = DEFAULT_SETTINGS['company_details']
            save_settings(config)

        print("\n" + "="*40)
        print("   PMTool: GLOBAL SETTINGS   ")
        print("="*40)
        print(f"1. GST Rate:           {config.get('gst_rate', 0.10)*100:.1f}%")
        print(f"2. Default Markup:     {config.get('markup_rate', 0.15)*100:.1f}%")
        print(f"3. Job ID Prefix:      {config.get('id_prefix', 'JN-')}")
        print(f"4. Next Start Number:  {config.get('start_number', 10000)}")
        print("5. View/Edit Standard Roles")
        print("6. View/Edit Standard Materials")
        print("7. Update Company Details (For PDFs)") # <-- NEW OPTION
        print("0. Back")
        
        choice = input("\nSelect: ").strip()
        
        if choice == '0': 
            break
        elif choice == '1':
            try:
                val = float(input("Enter new GST %: "))
                config['gst_rate'] = val / 100
                save_settings(config)
            except ValueError: print("!! Invalid input.")
        elif choice == '2':
            try:
                val = float(input("Enter new Default Markup %: "))
                config['markup_rate'] = val / 100
                save_settings(config)
            except ValueError: print("!! Invalid input.")
        elif choice == '3':
            config['id_prefix'] = input("Enter new prefix: ").strip()
            save_settings(config)
        elif choice == '4':
            try:
                config['start_number'] = int(input("Enter new start number: "))
                save_settings(config)
            except ValueError: print("!! Invalid input.")
        elif choice == '5':
            print(">> Use your config.json file to edit roles for now.")
        elif choice == '6':
            print("\n--- STANDARD MATERIALS & ASSEMBLIES ---")
            for m in config.get('standard_materials', []):
                if m.get('is_assembly'):
                    print(f"[*] {m['name']} (${m['cost']:.2f})")
                else:
                    print(f"[-] {m['name']} (${m['cost']:.2f})")
            input("\nPress Enter to return...")
        elif choice == '7':
            print("\n--- COMPANY DETAILS ---")
            print(" [*] Press Enter on any field to keep its current value.")
            comp = config.get('company_details', {})
            
            new_name = input(f"Company Name [{comp.get('name', 'N/A')}]: ").strip()
            if new_name: comp['name'] = new_name
            
            new_abn = input(f"ABN [{comp.get('abn', 'N/A')}]: ").strip()
            if new_abn: comp['abn'] = new_abn
            
            new_add = input(f"Address [{comp.get('address', 'N/A')}]: ").strip()
            if new_add: comp['address'] = new_add
            
            new_ph = input(f"Phone [{comp.get('phone', 'N/A')}]: ").strip()
            if new_ph: comp['phone'] = new_ph
            
            new_em = input(f"Email [{comp.get('email', 'N/A')}]: ").strip()
            if new_em: comp['email'] = new_em
            
            config['company_details'] = comp
            save_settings(config)
            print(">> Company details updated.")
            
        else:
            print("!! Invalid choice.")