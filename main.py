import engine
import storage

def get_labor_inputs():
    items = []
    print("\n--- LABOR BREAKDOWN (Type 'done') ---")
    while True:
        role = input("Role: ").strip().title()
        if role.lower() == 'done': break
        try:
            hrs = float(input(f"  Hours for {role}: "))
            rate = float(input(f"  Rate for {role} ($): "))
            items.append({"role": role, "hours": hrs, "rate": rate})
        except ValueError: print("  !! Invalid number.")
    return items

def get_material_inputs():
    items = []
    print("\n--- MATERIALS BREAKDOWN (Type 'done') ---")
    while True:
        name = input("Material Name: ").strip().title()
        if name.lower() == 'done': break
        try:
            price = float(input(f"  Cost for {name} ($): "))
            items.append({"name": name, "price": price})
        except ValueError: print("  !! Invalid number.")
    return items

def create_estimate():
    name = input("Project Name: ")
    scope = input("Scope: ")
    labor = get_labor_inputs()
    mats = get_material_inputs()
    base = engine.calculate_totals(labor, mats)
    tax = engine.calculate_gst(base['total_ex'])
    storage.save_to_db(name, scope, labor, mats, base['total_ex'], tax['gst_value'], tax['total_inc_gst'])
    print("\n>> Saved.")

def view_history_menu():
    while True:
        logs = storage.get_all_history()
        if not logs: break
        
        # ... (Print list of projects) ...
        
        choice = input("Select # for details (0 to exit): ")
        if choice == '0': break
        
        try:
            idx = int(choice) - 1
            selected = logs[idx]
            print("\n" + "="*60)
            print(f"PROJECT: {selected['Project'].upper()} | DATE: {selected.get('Timestamp')}")
            print(f"SCOPE: {selected.get('Scope')}")
            print("-" * 60)
            
            # Show Labor
            print(f"{'Role':<15} | {'Hrs':<5} | {'Rate':<10} | {'Subtotal':>12}")
            for l in selected.get('Labor', []):
                sub = l['hours'] * l['rate']
                print(f"{l['role']:<15} | {l['hours']:<5} | ${l['rate']:<9,.2f} | ${sub:11,.2f}")
            
            # Show Materials
            print("-" * 60)
            for m in selected.get('Materials', []):
                print(f"{m['name']:<45} | ${m['price']:11,.2f}")
            
            print("=" * 60)
            print(f"GRAND TOTAL (Inc GST): ${selected['Total_Inc_GST']:,.2f}")
            input("\nPress Enter...")
        except: print("Invalid Choice")

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