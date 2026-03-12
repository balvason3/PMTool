import json
import os

# --- THE "ENGINE" ---

def get_all_history():
    history = []
    if os.path.exists('budgets.json'):
        with open('budgets.json', 'r') as f:
            for line in f:
                if line.strip():
                    history.append(json.loads(line))
    return history

def get_project_by_index(index):
    history = get_all_history()
    if 0 <= index < len(history):
        return history[index]
    return None

# --- THE "INTERFACE" ---

def view_history_menu():
    logs = get_all_history()
    
    if not logs:
        print("\nNo records found.")
        input("Press Enter to return...")
        return

    while True:
        print("\n" + "-"*40)
        print(f"{'#':<3} | {'Project Name':<20} | {'Total (Inc)'}")
        print("-"*40)
        
        # We use enumerate to give each item a number (starting at 1 for humans)
        for i, entry in enumerate(logs, 1):
            total_inc = entry.get('Total_Inc_GST', 0)
            print(f"{i:<3} | {entry['Project']:<20} | ${total_inc:,.2f}")
        
        print("-"*40)
        print("Enter a number to see full details, or '0' to go back.")
        
        choice = input("\nSelect: ")
        
        if choice == '0':
            break
        
        try:
            idx = int(choice) - 1
            selected = get_project_by_index(idx)
            
            if selected:
                # FULL BREAKDOWN VIEW
                print("\n" + "="*30)
                print(f"DETAILS: {selected['Project'].upper()}")
                print("="*30)
                print(f"Base + Contingency: ${selected.get('Total_Ex_GST', 0):,.2f}")
                print(f"GST (10%):          ${selected.get('GST', 0):,.2f}")
                print(f"GRAND TOTAL:        ${selected.get('Total_Inc_GST', 0):,.2f}")
                print("="*30)
                input("\nPress Enter to return to list...")
            else:
                print("\n!! Invalid number.")
        except ValueError:
            print("\n!! Please enter a valid number.")

def main_menu():
    running = True 
    while running:
        print("\n" + "="*40)
        print("   PMTool: MAIN MENU   ")
        print("="*40)
        print("1. Create New Estimate")
        print("2. Manage History (Select Projects)")
        print("3. EXIT")
        
        choice = input("\nChoice: ")

        if choice == '1':
            # ... (your existing create logic remains here)
            pass 
        elif choice == '2':
            view_history_menu()
        elif choice == '3':
            running = False

if __name__ == "__main__":
    # Note: In your actual file, keep the create_budget logic from the previous step
    main_menu()