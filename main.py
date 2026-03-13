import engine
import storage
import labour  # Import your new file

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
        if not logs:
            print("\nNo records found.")
            input("Press Enter to return...")
            break
        
        # --- RESTORED PROJECT LIST ---
        print("\n" + "-"*45)
        print(f"{'#':<3} | {'Project Name':<20} | {'Total (Inc)'}")
        print("-"*45)
        
        for i, entry in enumerate(logs, 1):
            total_inc = entry.get('Total_Inc_GST', 0)
            print(f"{i:<3} | {entry['Project']:<20} | ${total_inc:,.2f}")
        
        print("-"*45)
        # -----------------------------

        choice = input("Select # for details (0 to exit): ")
        if choice == '0': 
            break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(logs):
                selected = logs[idx]
                print("\n" + "="*60)
                print(f"PROJECT: {selected['Project'].upper()} | DATE: {selected.get('Timestamp', 'N/A')}")
                print(f"SCOPE: {selected.get('Scope', 'N/A')}")
                print("-" * 60)
                
                # Show Labor
                print(f"{'Role':<15} | {'Hrs':<5} | {'Rate':<10} | {'Subtotal':>12}")
                for l in selected.get('Labor', []):
                    sub = l['hours'] * l['rate']
                    print(f"{l['role']:<15} | {l['hours']:<5} | ${l['rate']:<9,.2f} | ${sub:11,.2f}")
                
                # Show Materials
                print("\n" + f"{'Material Item':<43} | {'Cost':>12}")
                print("-" * 60)
                for m in selected.get('Materials', []):
                    print(f"{m['name']:<43} | ${m['price']:11,.2f}")
                
                print("=" * 60)
                print(f"GRAND TOTAL (Inc GST): ${selected.get('Total_Inc_GST', 0):,.2f}")
                print("=" * 60)
                
                print("\n1. Delete | 2. Back")
                action = input("Choice: ")
                if action == '1':
                    if input("Confirm Delete? (y/n): ").lower() == 'y':
                        storage.delete_project_by_index(idx)
                        # Don't break here, so it refreshes the list
            else:
                print("!! Invalid Selection.")
        except ValueError:
            print("!! Please enter a number.")

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