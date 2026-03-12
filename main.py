# --- PMTool: MAIN INTERFACE ---
import engine
import storage

def create_estimate():
    print("\n" + "-"*30)
    print("CREATE NEW ESTIMATE")
    print("-"*30)
    try:
        name = input("Project Name: ")
        hours = float(input("Labor Hours: "))
        rate = float(input("Hourly Rate ($): "))
        mats = float(input("Materials Cost (Ex-GST) ($): "))
        
        # We call the ENGINE for math
        base = engine.calculate_totals(hours, rate, mats)
        tax_data = engine.calculate_gst(base['total_ex'])
        
        # We call STORAGE to save
        storage.save_to_db(name, base['total_ex'], tax_data['gst_value'], tax_data['total_inc_gst'])
        
        print(f"\n>> SUCCESS: {name} saved.")
        print(f"Total (Ex-GST):  ${base['total_ex']:,.2f}")
        print(f"GST (10%):       ${tax_data['gst_value']:,.2f}")
        print(f"TOTAL (Inc-GST): ${tax_data['total_inc_gst']:,.2f}")
        input("\nPress Enter to return...")
    except ValueError:
        print("\n!! ERROR: Please enter numbers for hours, rate, and materials.")
        input("Press Enter to try again...")

def view_history_menu():
    while True:
        # Ask STORAGE for the data
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
                if action == '