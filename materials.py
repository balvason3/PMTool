import storage
import engine
import settings

def select_material_ui(config):
    """Displays the standard materials and returns the selected dictionary."""
    mats = config.get('standard_materials', [])
    print("\n--- SELECT MATERIAL ---")
    for i, m in enumerate(mats):
        tag = "[Assembly]" if m.get('is_assembly') else "[Item]"
        print(f"{i+1}. {tag} {m['name']} (${m.get('cost', 0.0):.2f})")
    print("C. Custom Material")
    print("0. Done / Cancel")
    
    while True:
        choice = input("Select #, 'C' for Custom, or '0': ").strip().upper()
        
        if choice == '0':
            return None
        elif choice == 'C':
            custom = input("Enter Custom Material Name: ").strip().title()
            if custom: return {"name": custom, "cost": 0.0, "is_assembly": False}
        elif choice.isdigit() and 0 < int(choice) <= len(mats):
            return mats[int(choice)-1]
            
        print("!! Invalid choice. Please try again.")

def get_labor_rate(config, role_name):
    """Helper to find the standard rate for a role."""
    for r in config.get('standard_roles', []):
        if r['name'].lower() == role_name.lower():
            return r.get('rate', 0.0)
    return 0.0

def get_material_inputs(labor_list):
    """UPDATED: Now takes labor_list so assemblies can inject hours."""
    config = settings.load_settings()
    default_markup = config['markup_rate'] * 100
    items = []
    
    print("\n--- MATERIALS BREAKDOWN ---")
    while True:
        mat_data = select_material_ui(config)
        if not mat_data: 
            break
            
        mat_name = mat_data['name']
        is_assembly = mat_data.get('is_assembly', False)
        unit = mat_data.get('unit', 'each')  # <-- Fetches the custom unit!
        
        try:
            markup_in = input(f"  Markup % (Press Enter for default {default_markup:.1f}%): ").strip()
            markup_pct = float(markup_in) if markup_in else default_markup

            # Logic for Custom items
            if mat_data['cost'] == 0.0:
                est_cost = float(input(f"  Total Estimated Cost for {mat_name} ($): "))
                items.append({"name": mat_name, "estimated_cost": est_cost, "actual_cost": 0.0, "markup_percent": markup_pct})
                
            # Logic for Standard Database Items & Assemblies
            else:
                # <-- The prompt now dynamically inserts the unit here:
                qty = float(input(f"  Enter Quantity ({unit}) for {mat_name}: "))
                
                base_cost = qty * mat_data['cost']
                items.append({"name": mat_name, "estimated_cost": base_cost, "actual_cost": 0.0, "markup_percent": markup_pct})
                
                # If it's an Assembly, trigger the Macro
                if is_assembly:
                    # 1. Add Consumables to Materials
                    consumable_cost = qty * mat_data.get('consumables_cost', 0.0)
                    if consumable_cost > 0:
                        items.append({
                            "name": f"Consumables ({mat_name})", 
                            "estimated_cost": consumable_cost, 
                            "actual_cost": 0.0, 
                            "markup_percent": markup_pct
                        })
                    
                    # 2. Inject Labor into the labor_list!
                    role = mat_data.get('labor_role', 'General Labor')
                    hrs = qty * mat_data.get('labor_hours', 0.0)
                    rate = get_labor_rate(config, role)
                    
                    labor_list.append({
                        "role": f"{role} (Assembly)", 
                        "estimated_hours": hrs, 
                        "actual_hours": 0.0, 
                        "rate": rate, 
                        "markup_percent": markup_pct
                    })
                    print(f"  >> Macro Triggered: Added {hrs:.1f}hrs of {role} and ${consumable_cost:.2f} in consumables.")

        except ValueError: 
            print("  !! Invalid number. Please retry.")
            
    return items

def log_materials_ui(selected_project, index):
    # Keeping this simple for now: Standard Variation Logging
    # We can upgrade this to handle variation assemblies later!
    config = settings.load_settings()
    default_markup = config['markup_rate'] * 100
    
    while True:
        print(f"\n--- LOG MATERIAL COSTS: {selected_project['Project']} ---")
        mats = selected_project.get('Materials', [])
        for i, m in enumerate(mats):
            print(f"{i+1}. {m['name']} (Spent so far: ${m.get('actual_cost', 0):,.2f})")
        
        choice = input("\nSelect Material # to log cost, 'N' for New Material, or '0' to exit: ").strip().upper()
        
        if choice == '0':
            break 
            
        elif choice == 'N':
            name = input("Enter new Custom Material name: ").strip().title()
            is_billable = input("Is this a billable variation? (y/n): ").strip().lower()
            
            try:
                if is_billable == 'y':
                    est_cost = float(input(f"Enter estimated COST for {name} ($): "))
                    markup_in = input(f"Markup % (Press Enter for default {default_markup:.1f}%): ").strip()
                    markup_pct = float(markup_in) if markup_in else default_markup
                    
                    mats.append({"name": name, "estimated_cost": est_cost, "actual_cost": 0.0, "variation": True, "billable": True, "markup_percent": markup_pct})
                else:
                    mats.append({"name": name, "estimated_cost": 0.0, "actual_cost": 0.0, "variation": True, "billable": False, "markup_percent": 0.0})
                
                labor = selected_project.get('Labor', [])
                base = engine.calculate_totals(labor, mats)
                tax = engine.calculate_gst(base['total_ex'])
                
                selected_project['Total_Ex_GST'] = base['total_ex']
                selected_project['GST'] = tax['gst_value']
                selected_project['Total_Inc_GST'] = tax['total_inc_gst']
                
                storage.update_project(index, selected_project)
                print(">> Variation Added.")
            except ValueError:
                print("!! Invalid input.")
            
        elif choice.isdigit() and int(choice) > 0:
            idx = int(choice) - 1
            if idx < len(mats):
                try:
                    added = float(input(f"Log invoice amount for {mats[idx]['name']} ($): "))
                    mats[idx]['actual_cost'] = mats[idx].get('actual_cost', 0) + added
                    storage.update_project(index, selected_project)
                    print(">> Material Cost Logged Successfully.")
                except ValueError:
                    print("!! Invalid number.")