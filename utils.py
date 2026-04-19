# --- PMTool: UTILITY FUNCTIONS MODULE ---
"""Shared utility functions to reduce code duplication across modules."""

def select_from_list(items, item_key_func, display_func, allow_custom=False, custom_processor=None):
    """
    Unified selection menu for roles, materials, suppliers, etc.
    
    Args:
        items: List of dictionaries to select from
        item_key_func: Function to get unique key from item (e.g., lambda x: x['name'])
        display_func: Function to display item (e.g., lambda i, x: f"{i+1}. {x['name']} (${x['rate']:.2f})")
        allow_custom: Whether to allow custom entry
        custom_processor: Function to process custom input (e.g., lambda x: {"name": x, "rate": 0.0})
    
    Returns:
        Selected item dictionary, or None if cancelled
    """
    print("\n--- SELECT ---")
    for i, item in enumerate(items):
        print(display_func(i, item))
    
    if allow_custom:
        print("C. Custom Entry")
    print("0. Done / Cancel")
    
    while True:
        choice = input("Select # (or 'C' for custom, '0' to cancel): ").strip().upper()
        
        if choice == '0':
            return None
        elif choice == 'C' and allow_custom:
            custom_input = input("Enter custom value: ").strip()
            if custom_input:
                if custom_processor:
                    return custom_processor(custom_input)
                else:
                    return {"name": custom_input, "value": 0.0}
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx]
        
        print("!! Invalid choice. Please try again.")


def select_role_from_config(config):
    """
    Select a role from the config's standard roles.
    Returns: Role dictionary or None
    """
    roles = config.get('standard_roles', [])
    
    def display(i, role):
        return f"{i+1}. {role['name']} (${role.get('rate', 0.0):.2f}/hr)"
    
    def custom_processor(name):
        return {"name": name.title(), "rate": 0.0}
    
    return select_from_list(
        roles,
        lambda x: x['name'],
        display,
        allow_custom=True,
        custom_processor=custom_processor
    )


def select_material_from_config(config):
    """
    Select a material from the config's standard materials.
    Returns: Material dictionary or None
    """
    materials = config.get('standard_materials', [])
    
    def display(i, mat):
        tag = "[*] Assembly" if mat.get('is_assembly') else "[-] Item"
        return f"{i+1}. {tag} {mat['name']} (${mat.get('cost', 0.0):.2f})"
    
    def custom_processor(name):
        return {"name": name.title(), "cost": 0.0, "is_assembly": False}
    
    return select_from_list(
        materials,
        lambda x: x['name'],
        display,
        allow_custom=True,
        custom_processor=custom_processor
    )


def select_supplier_from_list(suppliers, allow_new=True):
    """
    Select a supplier from the supplier list.
    Returns: Supplier name or None
    """
    print("\n--- SELECT SUPPLIER ---")
    if not suppliers:
        print(" [*] Database empty. You can type a new supplier name to add one.")
    
    for i, sup in enumerate(suppliers):
        print(f"{i+1}. {sup['name']}")
    
    print("0. Leave as TBA")
    
    choice = input("\nSelect Supplier # (or type a new Supplier Name): ").strip()
    
    if choice == '0':
        return "TBA"
    elif choice.isdigit() and 0 < int(choice) <= len(suppliers):
        return suppliers[int(choice)-1]['name']
    elif choice and not choice.isdigit():
        # User entered a new supplier name
        return choice
    else:
        print("!! Invalid entry. Defaulting to TBA.")
        return "TBA"


def safe_float_input(prompt, default=None):
    """
    Safely get float input from user.
    
    Args:
        prompt: Question to ask user
        default: Default value if user presses Enter
    
    Returns:
        Float value or None if invalid
    """
    try:
        user_input = input(prompt).strip()
        if not user_input and default is not None:
            return default
        return float(user_input) if user_input else None
    except ValueError:
        print("!! Invalid number. Please try again.")
        return None


def display_table(rows, headers, col_widths):
    """
    Display a formatted table.
    
    Args:
        rows: List of tuples or lists (one per row)
        headers: List of header strings
        col_widths: List of column widths
    """
    # Print headers
    header_line = " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        print(" | ".join(f"{str(cell):<{w}}" for cell, w in zip(row, col_widths)))
