# --- BEDROCK: GLOBAL SETTINGS (ORM) ---
import json
from database import AppSetting, StandardRole, StandardMaterial, get_session

# We keep CONFIG_FILE defined just to satisfy the startup_check in main.py temporarily 
# until we fully delete it.
CONFIG_FILE = "data/config.json" 

DEFAULT_SETTINGS = {
    "gst_rate": 0.10,
    "markup_rate": 0.15, 
    "id_prefix": "PJ-",
    "start_number": 10000,
    "quote_prefix": "QT-",
    "quote_start": 1000,
    "company_details": {
        "name": "YOUR COMPANY NAME",
        "abn": "XX XXX XXX XXX",
        "address": "123 Business Street",
        "phone": "0400 000 000",
        "email": "admin@yourcompany.com.au"
    }
}

def load_settings():
    """Loads settings from SQL and returns the expected dictionary."""
    config = {}
    for db in get_session():
        # 1. Load basic key-value settings
        settings_db = db.query(AppSetting).all()
        for setting in settings_db:
            config[setting.key] = json.loads(setting.value)
            
        # 2. Load Standard Roles
        roles_db = db.query(StandardRole).all()
        config['standard_roles'] = [{"name": r.name, "rate": r.rate} for r in roles_db]
        
        # 3. Load Standard Materials
        mats_db = db.query(StandardMaterial).all()
        config['standard_materials'] = [{
            "name": m.name, "cost": m.cost, "unit": m.unit,
            "is_assembly": m.is_assembly, "consumables_cost": m.consumables_cost,
            "labor_role": m.labor_role, "labor_hours": m.labor_hours
        } for m in mats_db]

        # Inject defaults if database is brand new
        needs_save = False
        for key, val in DEFAULT_SETTINGS.items():
            if key not in config and key != "standard_roles" and key != "standard_materials":
                config[key] = val
                needs_save = True
                
        if needs_save:
            save_settings(config)

    return config

def save_settings(settings_dict):
    """Saves the entire config dictionary back to the appropriate SQL tables."""
    for db in get_session():
        # 1. Save core key/values
        for key, val in settings_dict.items():
            if key in ["standard_roles", "standard_materials"]: continue
            
            existing = db.query(AppSetting).filter_by(key=key).first()
            if existing:
                existing.value = json.dumps(val)
            else:
                db.add(AppSetting(key=key, value=json.dumps(val)))
                
        # 2. Sync Standard Roles
        if "standard_roles" in settings_dict:
            db.query(StandardRole).delete()
            for r in settings_dict["standard_roles"]:
                db.add(StandardRole(name=r.get("name"), rate=r.get("rate", 0.0)))
                
        # 3. Sync Standard Materials
        if "standard_materials" in settings_dict:
            db.query(StandardMaterial).delete()
            for m in settings_dict["standard_materials"]:
                db.add(StandardMaterial(
                    name=m.get("name"), cost=m.get("cost", 0.0), unit=m.get("unit", "each"),
                    is_assembly=m.get("is_assembly", False), consumables_cost=m.get("consumables_cost", 0.0),
                    labor_role=m.get("labor_role"), labor_hours=m.get("labor_hours", 0.0)
                ))
        db.commit()

# --- THE REST OF YOUR SETTINGS UI FUNCTIONS GO BELOW HERE EXACTLY AS THEY WERE ---
# (manage_standard_roles_ui, manage_standard_materials_ui, run_first_time_setup, settings_menu_ui)
        
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