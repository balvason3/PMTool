# --- PMTool: SUPPLIER MANAGEMENT MODULE ---
import json
import os

SUPPLIERS_FILE = 'suppliers.json'

def load_suppliers():
    """Loads suppliers from the JSON file. Returns an empty list if it doesn't exist."""
    if not os.path.exists(SUPPLIERS_FILE):
        return []
    with open(SUPPLIERS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_suppliers(suppliers):
    """Saves the supplier list back to the JSON file."""
    with open(SUPPLIERS_FILE, 'w') as f:
        json.dump(suppliers, f, indent=4)

def add_supplier_ui():
    """UI for adding a new supplier with expanded details."""
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

def view_suppliers_ui():
    """Displays the list of all suppliers and their details."""
    suppliers = load_suppliers()
    if not suppliers:
        print("\n!! No suppliers found. Please add one first.")
        return
    
    print("\n" + "-"*80)
    print(f"{'#':<3} | {'Supplier Name':<25} | {'ABN':<15} | {'Phone'}")
    print("-" * 80)
    for i, sup in enumerate(suppliers):
        print(f"{i+1:<3} | {sup['name'][:25]:<25} | {sup['abn'][:15]:<15} | {sup['phone']}")
    print("-" * 80)
    
    input("\nPress Enter to return...")

def supplier_menu_ui():
    """Main menu for managing the supplier database."""
    while True:
        print("\n" + "="*40)
        print("   PMTool: SUPPLIER DATABASE   ")
        print("="*40)
        print("1. View All Suppliers")
        print("2. Add New Supplier")
        print("0. Back")
        
        choice = input("\nSelect: ").strip()
        if choice == '1': 
            view_suppliers_ui()
        elif choice == '2': 
            add_supplier_ui()
        elif choice == '0': 
            break
        else:
            print("!! Invalid choice.")