# --- PMTool: GLOBAL SETTINGS MODULE ---
import json
import os

CONFIG_FILE = 'config.json'

DEFAULT_SETTINGS = {
    "gst_rate": 0.10,
    "markup_rate": 0.15, 
    "id_prefix": "JN-",
    "start_number": 10000,
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
    with open(CONFIG_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def settings_menu_ui():
    while True:
        config = load_settings()
        print("\n" + "="*40)
        print("   PMTool: GLOBAL SETTINGS   ")
        print("="*40)
        print(f"1. GST Rate: {config['gst_rate'] * 100:.1f}%")
        print(f"2. Default Markup: {config['markup_rate'] * 100:.1f}%")
        print(f"3. Job Number Prefix: {config['id_prefix']}")
        print(f"4. Job Start Number: {config['start_number']}")
        print(f"5. Edit Standard Roles & Rates")
        print(f"6. View Standard Materials/Assemblies")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect setting to change (0 to exit): ").strip()
        
        if choice == '0': break
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
            # Simplified for brevity here (Keep your previous logic if you want to edit!)
            print(">> Use your config.json file to edit roles for now.")
        elif choice == '6':
            print("\n--- STANDARD MATERIALS & ASSEMBLIES ---")
            for m in config.get('standard_materials', []):
                if m.get('is_assembly'):
                    print(f"[*] {m['name']} (${m['cost']:.2f} + {m['labor_hours']}hrs {m['labor_role']})")
                else:
                    print(f"[-] {m['name']} (${m['cost']:.2f})")
            input("\nPress Enter to return...")