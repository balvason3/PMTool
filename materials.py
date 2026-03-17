# --- PMTool: MATERIALS MODULE ---

def get_material_inputs():
    """Handles the loop to collect baseline material estimates."""
    items = []
    print("\n--- MATERIALS BREAKDOWN (Type 'done') ---")
    while True:
        name = input("Material Name: ").strip().title()
        if name.lower() == 'done': break
        try:
            est_cost = float(input(f"  Estimated Cost for {name} ($): "))
            # Initialize with actual_cost: 0 for tracking
            items.append({
                "name": name, 
                "estimated_cost": est_cost, 
                "actual_cost": 0.0
            })
        except ValueError: 
            print("  !! Invalid number. Please retry.")
    return items