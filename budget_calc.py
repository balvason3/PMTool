import json
import os

# --- THE "ENGINE" (UI-Ready Logic) ---

def calculate_gst(amount):
    """Calculates 10% GST."""
    gst_amount = amount * 0.10
    return {
        "gst_value": gst_amount,
        "total_inc_gst": amount + gst_amount
    }

def calculate_totals(labor_hours, hourly_rate, materials_cost, contingency_rate=0.15):
    """Calculates subtotal and contingency (Ex-GST)."""
    subtotal_ex_gst = (labor_hours * hourly_rate) + materials_cost
    contingency_ex_gst = subtotal_ex_gst * contingency_rate
    total_ex_gst = subtotal_ex_gst + contingency_ex_gst
    return {
        "total_ex": total_ex_gst,
        "contingency": contingency_ex_gst
    }

def save_to_db(project_name, total_ex, gst, total_inc):
    """Saves data to the JSON 'database'."""
    budget_data = {
        "Project": project_name,
        "Total_Ex_GST": total_ex,
        "GST": gst,
        "Total_Inc_GST": total_inc
    }
    with open('budgets.json', 'a') as f:
        json.dump(budget_data, f)
        f.write('\n')

def get_all_history():
    """Reads all projects from the file."""
    history = []
    if os.path.exists('budgets.json'):
        with open('budgets.json', 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        history.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return history

def delete_project_by_index(index):
    """Removes a project from the file."""
    history = get_all_history()
    if 0 <= index < len(history):
        removed_item = history.pop(index)
        with open('budgets.json', 'w') as f:
            for entry in history:
                json.dump(entry, f)
                f.write('\n')
        return removed_item['Project']
    return None

# --- THE "INTERFACE" (The Menu System) ---

def create_estimate():
    print("\n" + "-"*30)
    print("CREATE NEW ESTIMATE")
    print("-"*30)
    try:
        name = input("Project Name: ")
        hours = float(input("Labor Hours: "))
        rate = float(input("Hourly Rate ($): "))
        mats = float(input("Materials Cost (Ex-GST) ($): "))
        
        base = calculate_totals(hours, rate, mats)
        tax_data = calculate_gst(base['total_ex'])
        
        save_to_db(name, base['total_ex'], tax_data['gst_value'], tax_data['total_inc_gst'])
        
        print(f"\n>> SUCCESS: {name} saved.")
        print(f"Total (Ex-GST):  ${base['total_ex']:,.2f}")
        print(f"GST (10%):       ${tax_data['gst_value']:,.2f}")
        print(f"TOTAL (Inc-GST): ${tax_data['total_inc_gst']:,.2f}")
        input("\nPress Enter to return to menu...")
    except ValueError:
        print("\n!! ERROR: Please enter numbers for hours, rate, and materials.")
        input("Press Enter to try again...")

def view_history_menu():
    while True:
        logs = get_all_history()
        if not logs:
            print("\nNo records found.")
            input("Press Enter to return...")
            break

        print("\n" + "-"*45)
        print(f"{'#':<3} | {'Project Name':<20} | {'Total (Inc)'}")
        print("-"*45)
        
        for i, entry in enumerate(logs, 1):
            total_inc = entry.get('Total_Inc_GST', entry.get('Total', 0))
            print(f"{i:<3} | {entry['Project']:<20} | ${total_inc:,.2f}")
        
        print("-"*45)
        choice = input("Enter # to view/manage, or '0' to go back: ")
        
        if choice == '0':
            break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(logs):
                selected = logs[idx]
                print("\n" + "="*35)
                print(f"DETAILS: {selected['Project'].upper()}")
                print("="*35)
                print(f"Base + Contingency: ${selected.get('Total_Ex_GST', 0):,.2f}")
                print(f"GST (10%):          ${selected.get('GST', 0):,.2f}")
                print(f"GRAND TOTAL (Inc):  ${selected.get('Total_Inc_GST', 0):,.2f}")
                print("="*35)
                print("1. Delete this project")
                print("2. Return to list")
                
                action = input("\nChoice: ")
                if action == '1':
                    confirm = input(f"Delete '{selected['Project']}'? (y/n): ")
                    if confirm.lower() == 'y':
                        delete_project_by_index(idx)
                        print("\n>> Project Deleted.")
                        input("Press Enter...")
                        break # Refresh the list
            else:
                print("\n!! Invalid selection.")
        except ValueError:
            print("\n!! Please enter a valid number.")

def main_menu():
    running = True 
    while running:
        print("\n" + "="*40)
        print("   PMTool: BUDGET MANAGER v1.0   ")
        print("="*40)
        print("1. Create New Estimate")
        print("2. Manage History (View/Delete)")
        print("3. EXIT")
        
        choice = input("\nSelect: ")

        if choice == '1':
            create_estimate()
        elif choice == '2':
            view_history_menu()
        elif choice == '3':
            print("\nShutting down... Goodbye!")
            running = False

if __name__ == "__main__":
    main_menu()