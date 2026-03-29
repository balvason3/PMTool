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
        
def manage_standard_roles_ui():
    """UI for viewing, adding, editing, and deleting standard roles."""
    while True:
        config = load_settings()
        roles = config.get('standard_roles', [])
        
        print("\n" + "="*40)
        print("   STANDARD ROLES DATABASE   ")
        print("="*40)
        if not roles:
            print("No standard roles found.")
        else:
            for i, r in enumerate(roles):
                print(f"{i+1}. {r['name']} (${r.get('rate', 0.0):.2f}/hr)")
        print("-" * 40)
        print("A. Add New Role")
        print("E. Edit Role")
        print("D. Delete Role")
        print("0. Back")
        
        choice = input("\nSelect an action: ").strip().upper()
        
        if choice == '0':
            break
            
        elif choice == 'A':
            name = input("Enter new role name: ").strip().title()
            if name:
                try:
                    rate = float(input(f"Enter hourly cost rate for {name}: $"))
                    roles.append({"name": name, "rate": rate})
                    config['standard_roles'] = roles
                    save_settings(config)
                    print(f">> Role '{name}' added successfully.")
                except ValueError:
                    print("!! Invalid rate entered.")
            else:
                print("!! Name cannot be empty.")
                
        elif choice == 'E':
            if not roles: continue
            num = input("Enter Role # to edit (0 to cancel): ").strip()
            if num == '0': continue
            
            if num.isdigit() and 0 < int(num) <= len(roles):
                idx = int(num) - 1
                target = roles[idx]
                print(f"\nEditing: {target['name']}")
                print(" [*] Press Enter on any field to keep its current value.")
                
                new_name = input(f"Name [{target['name']}]: ").strip().title()
                rate_in = input(f"Hourly Rate [${target.get('rate', 0.0):.2f}]: ").strip()
                
                if new_name: target['name'] = new_name
                if rate_in:
                    try:
                        target['rate'] = float(rate_in)
                    except ValueError:
                        print("!! Invalid rate entered. Keeping old rate.")
                        
                roles[idx] = target
                config['standard_roles'] = roles
                save_settings(config)
                print(">> Role updated.")
            else:
                print("!! Invalid selection.")
                
        elif choice == 'D':
            if not roles: continue
            num = input("Enter Role # to DELETE (0 to cancel): ").strip()
            if num == '0': continue
            
            if num.isdigit() and 0 < int(num) <= len(roles):
                idx = int(num) - 1
                target_name = roles[idx]['name']
                confirm = input(f"Are you SURE you want to delete '{target_name}'? (Y/N): ").strip().upper()
                if confirm == 'Y':
                    del roles[idx]
                    config['standard_roles'] = roles
                    save_settings(config)
                    print(f">> Role '{target_name}' deleted.")
            else:
                print("!! Invalid selection.")
        else:
            print("!! Invalid choice.")     

def manage_standard_materials_ui():
    """UI for viewing, adding, editing, and deleting standard materials and assemblies."""
    while True:
        config = load_settings()
        materials = config.get('standard_materials', [])
        
        print("\n" + "="*40)
        print("   STANDARD MATERIALS DATABASE   ")
        print("="*40)
        if not materials:
            print("No standard materials found.")
        else:
            for i, m in enumerate(materials):
                tag = "[*] Assembly" if m.get('is_assembly') else "[-] Material"
                unit = m.get('unit', 'each') # Falls back to 'each' for old items
                print(f"{i+1}. {tag}: {m['name']} (${m.get('cost', 0.0):.2f} / {unit})")
        print("-" * 40)
        print("A. Add New Material/Assembly")
        print("E. Edit Item")
        print("D. Delete Item")
        print("0. Back")
        
        choice = input("\nSelect an action: ").strip().upper()
        
        if choice == '0':
            break
            
        elif choice == 'A':
            name = input("Enter new material name: ").strip().title()
            if not name:
                print("!! Name cannot be empty.")
                continue
                
            try:
                unit = input("Enter unit of measurement (e.g., each, m, km, hr) [Default: each]: ").strip()
                if not unit: unit = "each"
                
                cost = float(input(f"Enter cost per {unit} for {name}: $"))
                is_assy_in = input("Is this an Assembly that requires labor? (Y/N): ").strip().upper()
                
                if is_assy_in == 'Y':
                    cons_cost = input("Enter additional consumables cost per unit (Press Enter for $0): ").strip()
                    cons_cost = float(cons_cost) if cons_cost else 0.0
                    
                    labor_role = input("Enter associated labor role (e.g., Electrician): ").strip().title()
                    labor_hrs = input(f"Enter labor hours per unit for {labor_role} (Press Enter for 0): ").strip()
                    labor_hrs = float(labor_hrs) if labor_hrs else 0.0
                    
                    materials.append({
                        "name": name, 
                        "cost": cost, 
                        "unit": unit,
                        "is_assembly": True,
                        "consumables_cost": cons_cost,
                        "labor_role": labor_role,
                        "labor_hours": labor_hrs
                    })
                else:
                    materials.append({"name": name, "cost": cost, "unit": unit, "is_assembly": False})
                    
                config['standard_materials'] = materials
                save_settings(config)
                print(f">> Item '{name}' added successfully.")
            except ValueError:
                print("!! Invalid number entered.")
                
        elif choice == 'E':
            if not materials: continue
            num = input("Enter Item # to edit (0 to cancel): ").strip()
            if num == '0': continue
            
            if num.isdigit() and 0 < int(num) <= len(materials):
                idx = int(num) - 1
                target = materials[idx]
                current_unit = target.get('unit', 'each')
                
                print(f"\nEditing: {target['name']}")
                print(" [*] Press Enter on any field to keep its current value.")
                
                new_name = input(f"Name [{target['name']}]: ").strip().title()
                unit_in = input(f"Unit of Measurement [{current_unit}]: ").strip()
                
                # Check the new unit so the cost prompt makes sense
                display_unit = unit_in if unit_in else current_unit
                cost_in = input(f"Cost per {display_unit} [${target.get('cost', 0.0):.2f}]: ").strip()
                
                if new_name: target['name'] = new_name
                if unit_in: target['unit'] = unit_in
                if cost_in:
                    try: target['cost'] = float(cost_in)
                    except ValueError: print("!! Invalid cost. Keeping old cost.")
                
                # If it is an assembly, prompt for the extra details
                if target.get('is_assembly'):
                    print("\n--- Assembly Details ---")
                    cons_in = input(f"Consumables Cost [${target.get('consumables_cost', 0.0):.2f}]: ").strip()
                    role_in = input(f"Labor Role [{target.get('labor_role', '')}]: ").strip().title()
                    hrs_in = input(f"Labor Hours [{target.get('labor_hours', 0.0)}]: ").strip()
                    
                    if cons_in:
                        try: target['consumables_cost'] = float(cons_in)
                        except ValueError: pass
                    if role_in: target['labor_role'] = role_in
                    if hrs_in:
                        try: target['labor_hours'] = float(hrs_in)
                        except ValueError: pass
                        
                materials[idx] = target
                config['standard_materials'] = materials
                save_settings(config)
                print(">> Item updated.")
            else:
                print("!! Invalid selection.")
                
        elif choice == 'D':
            if not materials: continue
            num = input("Enter Item # to DELETE (0 to cancel): ").strip()
            if num == '0': continue
            
            if num.isdigit() and 0 < int(num) <= len(materials):
                idx = int(num) - 1
                target_name = materials[idx]['name']
                confirm = input(f"Are you SURE you want to delete '{target_name}'? (Y/N): ").strip().upper()
                if confirm == 'Y':
                    del materials[idx]
                    config['standard_materials'] = materials
                    save_settings(config)
                    print(f">> Item '{target_name}' deleted.")
            else:
                print("!! Invalid selection.")
        else:
            print("!! Invalid choice.")    

def run_first_time_setup():
    """Gathers initial company info for the config file."""
    print("\n" + "="*50)
    print("   INITIAL SETUP: COMPANY DETAILS   ")
    print("="*50)
    print("These details will be used to brand your PDF Purchase Orders.")
    print("You can press Enter to skip any field and fill it later.\n")
    
    # This automatically creates the default config.json if it's missing
    config = load_settings()
    comp = config.get('company_details', {})
    
    name = input(f"Company Name [{comp.get('name', '')}]: ").strip()
    abn = input(f"ABN [{comp.get('abn', '')}]: ").strip()
    address = input(f"Address [{comp.get('address', '')}]: ").strip()
    phone = input(f"Phone [{comp.get('phone', '')}]: ").strip()
    email = input(f"Email [{comp.get('email', '')}]: ").strip()
    
    if name: comp['name'] = name
    if abn: comp['abn'] = abn
    if address: comp['address'] = address
    if phone: comp['phone'] = phone
    if email: comp['email'] = email
    
    config['company_details'] = comp
    save_settings(config)
    print("\n>> Setup Complete! You can change these anytime in the Global Settings.")            

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
        print("7. Update Company Details (For PDFs)")
        print("8. Re-run Setup Wizard & Tutorial")
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
            manage_standard_roles_ui()
        elif choice == '6':
            manage_standard_materials_ui()
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
            
        elif choice == '8':
            demo = input("\nWould you like to view the tutorial? (Y/N): ").strip().upper()
            if demo == 'Y':
                import tutorial
                tutorial.run_demo()
            run_first_time_setup()
            
        else:
            print("!! Invalid choice.")