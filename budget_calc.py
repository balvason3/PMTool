

import json
import os

# --- THE "ENGINE" (UI-Ready) ---

def calculate_totals(labor_hours, hourly_rate, materials_cost, contingency_rate=0.15):
    subtotal = (labor_hours * hourly_rate) + materials_cost
    contingency = subtotal * contingency_rate
    return {
        "subtotal": subtotal,
        "contingency": contingency,
        "total": subtotal + contingency
    }

def save_to_db(project_name, total_amount):
    budget_data = {"Project": project_name, "Total": total_amount}
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

# --- THE "INTERFACE" (The Loop) ---

def main_menu():
    # This loop keeps the program alive until Option 3 is chosen
    running = True 
    
    while running:
        print("\n" + "="*30)
        print("   PMTool: BUDGET MANAGER   ")
        print("="*30)
        print("1. Create New Estimate")
        print("2. View History")
        print("3. EXIT PROGRAM")
        print("-"*30)
        
        choice = input("Select an option (1-3): ")

        if choice == '1':
            try:
                name = input("\nProject Name: ")
                hours = float(input("Estimated Labor Hours: "))
                rate = float(input("Hourly Rate ($): "))
                mats = float(input("Materials Cost ($): "))
                
                results = calculate_totals(hours, rate, mats)
                save_to_db(name, results['total'])
                
                print(f"\n>> SUCCESS: {name} saved.")
                print(f">> Total (Inc 15% Contingency): ${results['total']:,.2f}")
            except ValueError:
                print("\n!! ERROR: Please enter numbers for hours, rate, and materials.")

        elif choice == '2':
            logs = get_all_history()
            print("\n--- HISTORICAL LOGS ---")
            if not logs:
                print("No records found.")
            for entry in logs:
                print(f"Project: {entry['Project']:<20} | Total: ${entry['Total']:,.2f}")
            
            input("\nPress Enter to return to menu...")

        elif choice == '3':
            print("\nShutting down PMTool... Goodbye!")
            running = False # This breaks the loop and closes the script

        else:
            print("\n!! Invalid selection. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main_menu()