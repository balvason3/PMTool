# --- PMTool: MAIN INTERFACE ---
import engine
import storage

# --- HELPERS (Keep these above the main functions) ---

def get_labor_inputs():
    items = []
    print("\n--- LABOR BREAKDOWN (Type 'done' to finish) ---")
    while True:
        role = input("Role (e.g. PM, Trade, Admin) or 'done': ").strip().title()
        if role.lower() == 'done': break
        try:
            hrs = float(input(f"  Hours for {role}: "))
            rate = float(input(f"  Hourly Rate for {role} ($): "))
            items.append({"role": role, "hours": hrs, "rate": rate})
        except ValueError:
            print("  !! Invalid number. Try again.")
    return items

def get_material_inputs():
    items = []
    print("\n--- MATERIALS BREAKDOWN (Type 'done' to finish) ---")
    while True:
        name = input("Material Name or 'done': ").strip().title()
        if name.lower() == 'done': break
        try:
            price = float(input(f"  Cost for {name} ($): "))
            items.append({"name": name, "price": price})
        except ValueError:
            print("  !! Invalid number. Try again.")
    return items

# --- MAIN FUNCTIONS ---

def create_estimate():
    print("\n" + "="*30)
    print("NEW PROJECT ESTIMATE")
    print("="*30)
    try:
        name = input("Project Name: ")
        scope = input("Scope of Work: ")
        
        # We use our new helpers here
        labor_list = get_labor_inputs()
        materials_list = get_material_inputs()
        
        # Math logic (Ensure engine.calculate_totals accepts these two lists)
        base = engine.calculate_totals(labor_list, materials_list)
        tax = engine.calculate_gst(base['total_ex'])
        
        # Save to JSON (Ensure storage.save_to_db matches these arguments)
        storage.save_to_db(name, scope, labor_list, materials_list, 
                           base['total_ex'], tax['gst_value'], tax['total_inc_gst'])
        
        print(f"\n>> SUCCESS: {name} saved.")
        input("\nPress Enter to return to menu...")
    except ValueError:
        print("\n!! ERROR: Please enter valid numbers.")

def view_history_menu():
    while True:
        logs = storage.get_all_history()
        
        if not logs:
            print("\nNo records found.")
            input("Press Enter to return...")
            break

        print("\n" + "-"*45)
        print(f"{'#':<3} | {'Project Name':<20} | {'Total (Inc)'}")
        print("-"*45)
        
        for i, entry in enumerate(logs, 1):
            total_inc = entry.get('Total_Inc_GST', 0)
            print(f"{i:<3} | {entry['Project']:<20} | ${total_inc:,.2f}")
        
        print("-"*45)
        choice = input("Enter # to view details, or '0' to go back: ")
        
        if choice == '0':
            break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(logs):
                selected = logs[idx]
                
                print("\n" + "="*60)
                print(f"PROJECT: {selected['Project'].upper()}")
                print(f"DATE:    {selected.get('Timestamp', 'N/A')}")
                print(f"SCOPE:   {selected.get('Scope', 'N/A')}")
                print("="*60)
                
                # --- LABOR TABLE ---
                print(f"{'Role':<15} | {'Hrs':<6} | {'Rate':<10} | {'Subtotal':>12}")
                print("-" * 60)
                labor = selected.get('Labor', [])
                for l in labor:
                    sub = l['hours'] * l['rate']
                    print(f"{l['role']:<15} | {l['hours']:<6} | ${l['rate']:<9,.2f} | ${sub:11,.2f}")
                
                # --- MATERIALS TABLE ---
                print("\n" + f"{'Material Item':<43} | {'Cost':>12}")
                print("-" * 60)
                mats = selected.get('Materials', [])
                for m in mats:
                    print(f"{m['name']:<43} | ${m['price']:11,.2f}")
                
                print("-" * 60)
                
                # --- TOTALS ---
                labour_total = sum(l['hours'] * l['rate'] for l in labor)
                mats_total = sum(m['price'] for m in mats)
                
                print(f"{'Labor Subtotal:':<43} | ${labour_total:11,.2f}")
                print(f"{'Materials Subtotal:':<43} | ${mats_total:11,.2f}")
                print(f"{'Total (Ex-GST + Contingency):':<43} | ${selected.get('Total_Ex_GST', 0):11,.2f}")
                print(f"{'GST (10%):':<43} | ${selected.get('GST', 0):11,.2f}")
                print("="*60)
                print(f"{'GRAND TOTAL (Inc-GST):':<43} | ${selected.get('Total_Inc_GST', 0):11,.2f}")
                print("="*60)
                
                print("\n1. Delete | 2. Back")
                action = input("Choice: ")
                if action == '1':
                    if input("Confirm Delete? (y/n): ").lower() == 'y':
                        storage.delete_project_by_index(idx)
                        break
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")

def main_menu():
    while True:
        print("\n" + "="*40)
        print("   PMTool: MAIN MENU (Modular)   ")
        print("="*40)
        print("1. Create New Estimate")
        print("2. Manage History")
        print("3. EXIT")
        
        choice = input("\nSelect: ")

        if choice == '1':
            create_estimate()
        elif choice == '2':
            view_history_menu()
        elif choice == '3':
            print("\nShutting down... Goodbye!")
            break

if __name__ == "__main__":
    main_menu()