import storage
import engine
import settings

def select_role_ui(config):
    """Displays the standard roles and returns the selected dictionary."""
    roles = config.get('standard_roles', [])
    print("\n--- SELECT ROLE ---")
    for i, r in enumerate(roles):
        print(f"{i+1}. {r['name']} (${r.get('rate', 0.0):.2f}/hr)")
    print("C. Custom Role")
    print("0. Done / Cancel")
    
    while True:
        choice = input("Select #, 'C' for Custom, or '0': ").strip().upper()
        
        if choice == '0':
            return None
        elif choice == 'C':
            custom = input("Enter Custom Role Name: ").strip().title()
            # Custom roles have no default rate
            if custom: return {"name": custom, "rate": 0.0}
        elif choice.isdigit() and 0 < int(choice) <= len(roles):
            return roles[int(choice)-1]
            
        print("!! Invalid choice. Please try again.")

def get_labour_inputs():
    config = settings.load_settings()
    default_markup = config['markup_rate'] * 100
    items = []
    
    print("\n--- LABOUR ESTIMATE (Baseline) ---")
    while True:
        role_data = select_role_ui(config)
        if not role_data: 
            break 
            
        role_name = role_data['name']
        default_rate = role_data.get('rate', 0.0)
            
        try:
            hrs = float(input(f"  Estimated Hours for {role_name}: "))
            
            # If the database has a price, offer it as a default fallback
            if default_rate > 0:
                rate_in = input(f"  Hourly COST Rate for {role_name} (Press Enter for ${default_rate:.2f}): ").strip()
                rate = float(rate_in) if rate_in else default_rate
            else:
                rate = float(input(f"  Hourly COST Rate for {role_name} ($): "))
                
            markup_in = input(f"  Markup % (Press Enter for default {default_markup:.1f}%): ").strip()
            markup_pct = float(markup_in) if markup_in else default_markup
            
            items.append({"role": role_name, "estimated_hours": hrs, "actual_hours": 0.0, "rate": rate, "markup_percent": markup_pct})
        except ValueError:
            print("  !! Invalid number. Please retry.")
    return items

def log_hours_ui(selected_project, index):
    config = settings.load_settings()
    default_markup = config['markup_rate'] * 100
    
    while True:
        print(f"\n--- LOG HOURS: {selected_project['Project']} ---")
        labor = selected_project.get('Labor', [])
        for i, l in enumerate(labor):
            print(f"{i+1}. {l['role']} (Current: {l.get('actual_hours', 0)} hrs)")
        
        choice = input("\nSelect Role # to log hours, 'N' for New Role, or '0' to exit: ").strip().upper()
        
        if choice == '0':
            break 
            
        elif choice == 'N':
            role_data = select_role_ui(config)
            if not role_data:
                continue 
                
            role_name = role_data['name']
            default_rate = role_data.get('rate', 0.0)
                
            try:
                # Same fallback logic for variations
                if default_rate > 0:
                    rate_in = input(f"Enter hourly COST rate for {role_name} (Press Enter for ${default_rate:.2f}): ").strip()
                    rate = float(rate_in) if rate_in else default_rate
                else:
                    rate = float(input(f"Enter hourly COST rate for {role_name} ($): "))
                    
                is_billable = input("Is this a billable variation to the customer? (y/n): ").strip().lower()
                
                if is_billable == 'y':
                    est_hrs = float(input("Enter estimated hours for this variation: "))
                    markup_in = input(f"Markup % (Press Enter for default {default_markup:.1f}%): ").strip()
                    markup_pct = float(markup_in) if markup_in else default_markup
                    
                    labor.append({"role": role_name, "estimated_hours": est_hrs, "actual_hours": 0.0, "rate": rate, "variation": True, "billable": True, "markup_percent": markup_pct})
                    print(f">> Billable variation added. Project budget will increase.")
                else:
                    labor.append({"role": role_name, "estimated_hours": 0.0, "actual_hours": 0.0, "rate": rate, "variation": True, "billable": False, "markup_percent": 0.0})
                    print(f">> Non-billable role added. This will track as a project variance (loss).")
                
                mats = selected_project.get('Materials', [])
                base = engine.calculate_totals(labor, mats)
                tax = engine.calculate_gst(base['total_ex'])
                
                selected_project['Total_Ex_GST'] = base['total_ex']
                selected_project['GST'] = tax['gst_value']
                selected_project['Total_Inc_GST'] = tax['total_inc_gst']
                
                storage.update_project(index, selected_project)
                
            except ValueError:
                print("!! Invalid input. Please try again.")
                
        elif choice.isdigit() and int(choice) > 0:
            idx = int(choice) - 1
            if idx < len(labor):
                try:
                    added = float(input(f"Add how many hours to {labor[idx]['role']}? "))
                    current = labor[idx].get('actual_hours', 0)
                    labor[idx]['actual_hours'] = current + added
                    storage.update_project(index, selected_project)
                    print(">> Hours Logged Successfully.")
                except ValueError:
                    print("!! Invalid number.")