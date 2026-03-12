import json
import os

# --- THE "ENGINE" (UI-Ready) ---

def calculate_gst(amount):
    """Calculates 10% GST. Returns a dictionary with tax and total."""
    gst_amount = amount * 0.10
    return {
        "gst_value": gst_amount,
        "total_inc_gst": amount + gst_amount
    }

def calculate_totals(labor_hours, hourly_rate, materials_cost, contingency_rate=0.15):
    """Calculates subtotal and contingency. All values here are Ex-GST."""
    subtotal_ex_gst = (labor_hours * hourly_rate) + materials_cost
    contingency_ex_gst = subtotal_ex_gst * contingency_rate
    total_ex_gst = subtotal_ex_gst + contingency_ex_gst
    
    return {
        "subtotal_ex": subtotal_ex_gst,
        "contingency_ex": contingency_ex_gst,
        "total_ex": total_ex_gst
    }

def save_to_db(project_name, total_ex, gst, total_inc):
    """Saves a detailed record for future UI recall."""
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
    history = []
    if os.path.exists('budgets.json'):
        with open('budgets.json', 'r') as f:
            for line in f:
                if line.strip():
                    history.append(json.loads(line))
    return history

# --- THE "INTERFACE" ---

def main_menu():
    running = True 
    while running:
        print("\n" + "="*40)
        print("   PMTool: BUDGET MANAGER (AUD)   ")
        print("="*40)
        print("1. Create New Estimate")
        print("2. View History")
        print("3. EXIT")
        print("-" * 40)
        
        choice = input("Select an option (1-3): ")

        if choice == '1':
            try:
                name = input("\nProject Name: ")
                hours = float(input("Labor Hours: "))
                rate = float(input("Hourly Rate ($): "))
                mats = float(input("Materials Cost (Ex-GST) ($): "))
                
                # 1. Calculate the base budget (Ex-GST)
                base = calculate_totals(hours, rate, mats)
                
                # 2. Calculate the GST
                tax_data = calculate_gst(base['total_ex'])
                
                # 3. Save to database
                save_to_db(name, base['total_ex'], tax_data['gst_value'], tax_data['total_inc_gst'])
                
                # 4. Display to user
                print(f"\n>> BUDGET BREAKDOWN: {name}")
                print(f"Total (Ex-GST):   ${base['total_ex']:,.2f}")
                print(f"GST (10%):        ${tax_data['gst_value']:,.2f}")
                print(f"TOTAL (Inc-GST):  ${tax_data['total_inc_gst']:,.2f}")
                
            except ValueError:
                print("\n!! ERROR: Invalid input. Please use numbers.")

        elif choice == '2':
            logs = get_all_history()
            print("\n--- HISTORICAL LOGS ---")
            if not logs:
                print("No records found.")
            for entry in logs:
                # Note: Newer entries will have GST data, older ones won't. 
                # We use .get() to prevent crashing on old test data.
                total_inc = entry.get('Total_Inc_GST', entry.get('Total', 0))
                print(f"Project: {entry['Project']:<15} | Inc-GST: ${total_inc:,.2f}")
            
            input("\nPress Enter to return to menu...")

        elif choice == '3':
            print("\nShutting down... Goodbye!")
            running = False

if __name__ == "__main__":
    main_menu()