# --- BEDROCK: SUPPLIER MANAGEMENT (ORM) ---
from database import Supplier, get_session

def load_suppliers():
    """Loads suppliers directly from the SQL database."""
    suppliers_list = []
    for db in get_session():
        suppliers = db.query(Supplier).all()
        for sup in suppliers:
            suppliers_list.append({
                "id": sup.id, # Keep tracking the SQL ID
                "name": sup.name,
                "abn": sup.abn,
                "phone": sup.phone,
                "address": sup.address,
                "payment_details": sup.payment_details
            })
    return suppliers_list

def save_suppliers(suppliers_list):
    """
    Overwrites the supplier table to match the provided list. 
    Maintains compatibility with your current UI logic.
    """
    for db in get_session():
        db.query(Supplier).delete() # Wipe existing
        for sup in suppliers_list:
            new_sup = Supplier(
                name=sup.get('name'),
                abn=sup.get('abn', 'N/A'),
                phone=sup.get('phone', 'N/A'),
                address=sup.get('address', 'N/A'),
                payment_details=sup.get('payment_details', 'N/A')
            )
            db.add(new_sup)
        db.commit()

def add_supplier_ui():
    print("\n--- ADD NEW SUPPLIER ---")
    name = input("Supplier Name (Required): ").strip()
    if not name:
        print("!! Name is required. Canceling.")
        return
    
    abn = input("ABN (Press Enter to skip): ").strip()
    phone = input("Contact Phone (Press Enter to skip): ").strip()
    address = input("Address (Press Enter to skip): ").strip()
    payment = input("Payment Terms/Details (Press Enter to skip): ").strip()

    new_sup = {
        "name": name,
        "abn": abn if abn else "N/A",
        "phone": phone if phone else "N/A",
        "address": address if address else "N/A",
        "payment_details": payment if payment else "N/A"
    }

    suppliers = load_suppliers()
    suppliers.append(new_sup)
    save_suppliers(suppliers)
    print(f">> Supplier '{name}' saved successfully.")
    
def add_supplier_inline(name):
    print(f"\n--- ADDING NEW SUPPLIER: {name.upper()} ---")
    abn = input("ABN (Press Enter to skip): ").strip()
    phone = input("Contact Phone (Press Enter to skip): ").strip()
    address = input("Address (Press Enter to skip): ").strip()
    payment = input("Payment Terms/Details (Press Enter to skip): ").strip()

    new_sup = {
        "name": name,
        "abn": abn if abn else "N/A",
        "phone": phone if phone else "N/A",
        "address": address if address else "N/A",
        "payment_details": payment if payment else "N/A"
    }

    suppliers = load_suppliers()
    suppliers.append(new_sup)
    save_suppliers(suppliers)
    print(f">> Supplier '{name}' saved to database.")
    return name

def view_suppliers_ui():
    while True:
        suppliers = load_suppliers()
        if not suppliers:
            print("\n!! No suppliers found. Please add one first.")
            return
        
        print("\n" + "="*80)
        print("   SUPPLIER DIRECTORY   ")
        print("=" * 80)
        print(f"{'#':<3} | {'Supplier Name':<30} | {'Phone':<15} | {'ABN'}")
        print("-" * 80)
        for i, sup in enumerate(suppliers):
            name = sup.get('name', 'Unknown')[:30]
            phone = sup.get('phone', 'N/A')[:15]
            abn = sup.get('abn', 'N/A')[:20]
            print(f"{i+1:<3} | {name:<30} | {phone:<15} | {abn}")
        print("-" * 80)
        
        choice = input("\nEnter Supplier # for more details, or '0' to go back: ").strip()
        if choice == '0': break
            
        if choice.isdigit() and 0 < int(choice) <= len(suppliers):
            selected = suppliers[int(choice)-1]
            print("\n" + "*"*50)
            print(f"   SUPPLIER PROFILE: {selected.get('name', 'Unknown').upper()}   ")
            print("*"*50)
            print(f"Name:            {selected.get('name', 'N/A')}")
            print(f"ABN:             {selected.get('abn', 'N/A')}")
            print(f"Phone:           {selected.get('phone', 'N/A')}")
            print(f"Address:         {selected.get('address', 'N/A')}")
            print(f"Payment Details: {selected.get('payment_details', 'N/A')}")
            print("*"*50)
            input("\nPress Enter to return to the directory...")
        else:
            print("!! Invalid selection.")
            
def edit_supplier_ui():
    suppliers = load_suppliers()
    if not suppliers: return

    print("\n--- EDIT SUPPLIER ---")
    for i, sup in enumerate(suppliers):
        print(f"{i+1}. {sup.get('name', 'Unknown')}")
        
    choice = input("\nSelect Supplier # to edit (0 to cancel): ").strip()
    if choice == '0': return
        
    if choice.isdigit() and 0 < int(choice) <= len(suppliers):
        idx = int(choice) - 1
        target = suppliers[idx]
        
        print(f"\nEditing: {target.get('name')}")
        print(" [*] Press Enter on any field to keep its current value.")
        
        name = input(f"Name [{target.get('name')}]: ").strip()
        abn = input(f"ABN [{target.get('abn', 'N/A')}]: ").strip()
        phone = input(f"Phone [{target.get('phone', 'N/A')}]: ").strip()
        address = input(f"Address [{target.get('address', 'N/A')}]: ").strip()
        payment = input(f"Payment Details [{target.get('payment_details', 'N/A')}]: ").strip()
        
        if name: target['name'] = name
        if abn: target['abn'] = abn
        if phone: target['phone'] = phone
        if address: target['address'] = address
        if payment: target['payment_details'] = payment
        
        suppliers[idx] = target
        save_suppliers(suppliers)
        print(f">> Supplier '{target['name']}' updated.")
    else:
        print("!! Invalid selection.")

def delete_supplier_ui():
    suppliers = load_suppliers()
    if not suppliers: return

    print("\n--- DELETE SUPPLIER ---")
    for i, sup in enumerate(suppliers):
        print(f"{i+1}. {sup.get('name', 'Unknown')}")
        
    choice = input("\nSelect Supplier # to DELETE (0 to cancel): ").strip()
    if choice == '0': return
        
    if choice.isdigit() and 0 < int(choice) <= len(suppliers):
        idx = int(choice) - 1
        target_name = suppliers[idx].get('name', 'Unknown')
        
        confirm = input(f"Are you SURE you want to delete '{target_name}'? (Y/N): ").strip().upper()
        if confirm == 'Y':
            del suppliers[idx]
            save_suppliers(suppliers)
            print(f">> Supplier '{target_name}' deleted.")
    else:
        print("!! Invalid selection.")

def supplier_menu_ui():
    while True:
        print("\n" + "="*40)
        print("   BEDROCK: SUPPLIER DATABASE   ")
        print("="*40)
        print("1. View All Suppliers")
        print("2. Add New Supplier")
        print("3. Edit Supplier")    
        print("4. Delete Supplier")  
        print("0. Back")
        
        choice = input("\nSelect: ").strip()
        if choice == '1': view_suppliers_ui()
        elif choice == '2': add_supplier_ui()
        elif choice == '3': edit_supplier_ui()
        elif choice == '4': delete_supplier_ui()
        elif choice == '0': break