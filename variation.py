# --- BEDROCK: VARIATIONS MODULE ---
import storage
import labour
import materials
import settings
import variation_generator

def variations_menu(selected, current_user):
    """Shows all variations for a project and provides options to add or update."""
    while True:
        internal_id = selected.get('internal_id')
        display_id = selected.get('Project_ID') or selected.get('Quote_Number')
        project_name = selected.get('Project')

        variations = storage.get_variations_by_project(internal_id)

        print(f"\n--- VARIATIONS | {display_id} | {project_name} ---")
        print("-" * 95)
        print(f"{'Ref':<6} | {'Status':<15} | {'Reason':<20} | {'Cost':>12} | {'Labour':>8} | {'Materials':>10} | {'Raised':<15}")
        print("-" * 95)

        if not variations:
            print("No variations found for this project.")
        else:
            for v in variations:
                labour_count = len(v.get('Labor', []))
                material_count = len(v.get('Materials', []))
                print(f"{v['reference']:<6} | {v['status']:<15} | {v['reason']:<20} | ${v['cost_impact']:>11,.2f} | {labour_count:>8} | {material_count:>10} | {v['raised_by']:<15}")

        print("-" * 95)
        print("1. Add New Variation")
        print("2. View/Update Variation")
        print("3. Generate PDF")
        print("0. Back")

        choice = input("\nSelect: ").strip()

        if choice == '1':
            add_variation_ui(selected, current_user)
        elif choice == '2':
            update_variation_ui(selected, current_user)
        elif choice == '3':
            generate_variation_pdf_ui(selected, current_user)
        elif choice == '0':
            break

def generate_variation_pdf_ui(selected, current_user):
    """Wrapper to generate variation PDF."""
    variation_generator.generate_variation_pdf_ui(selected, current_user)

def add_variation_ui(selected, current_user):
    """Collects inputs from PM and creates a new variation with labour and materials breakdown."""
    internal_id = selected.get('internal_id')
    display_id = selected.get('Project_ID') or selected.get('Quote_Number')
    project_name = selected.get('Project')

    print(f"\n--- NEW VARIATION | {display_id} | {project_name} ---")

    scope = input("Scope of variation: ").strip()
    if not scope:
        print("!! Scope cannot be empty.")
        return

    reason_map = {
        "1": "Client Request",
        "2": "Latent Condition",
        "3": "Design Change"
    }
    print("\n--- REASON ---")
    print("1. Client Request")
    print("2. Latent Condition")
    print("3. Design Change")
    reason_choice = input("Select reason: ").strip()
    reason = reason_map.get(reason_choice, "Client Request")

    # Load config for labour and materials input
    config = settings.load_settings()
    
    # Get labour items
    print("\n--- LABOUR (Press Enter to skip) ---")
    labor = []
    while True:
        continue_input = input("Add labour item? (Y/N, default N): ").strip().upper()
        if continue_input != 'Y':
            break
        labor_item = labour.get_labour_single_item(config)
        if labor_item:
            labor.append(labor_item)
    
    # Get materials items
    print("\n--- MATERIALS (Press Enter to skip) ---")
    mats = []
    while True:
        continue_input = input("Add material item? (Y/N, default N): ").strip().upper()
        if continue_input != 'Y':
            break
        mat_item = materials.get_material_single_item(config)
        if mat_item:
            mats.append(mat_item)
    
    # Calculate cost impact
    labour_total = sum(item.get('hours', 0) * item.get('rate', 0) for item in labor)
    materials_total = sum(item.get('quantity', 0) * item.get('unit_cost', 0) for item in mats)
    cost_impact = labour_total + materials_total

    programme_impact = input("\nProgramme impact (or leave blank): ").strip()

    ref = storage.save_variation(internal_id, current_user, scope, reason, cost_impact, programme_impact, labor, mats)
    print(f">> {ref} created successfully with ${cost_impact:,.2f} cost impact.")

def update_variation_ui(selected, current_user):
    """Lets PM pick a variation to view details or update its status."""
    internal_id = selected.get('internal_id')
    variations = storage.get_variations_by_project(internal_id)

    if not variations:
        print("!! No variations found for this project.")
        return

    while True:
        print("\n--- VIEW/UPDATE VARIATION ---")
        for i, v in enumerate(variations):
            print(f"{i+1}. {v['reference']} | {v['status']} | {v['scope_description'][:40]}")
        
        print("0. Back")
        choice = input("\nSelect variation # (or 0 to back): ").strip()
        
        if choice == '0':
            break
        
        if not (choice.isdigit() and 0 < int(choice) <= len(variations)):
            continue
        
        selected_var = variations[int(choice)-1]
        
        # Show details
        print(f"\n--- VARIATION {selected_var['reference']} ---")
        print(f"Status: {selected_var['status']}")
        print(f"Raised: {selected_var['raised_date']} by {selected_var['raised_by']}")
        print(f"Reason: {selected_var['reason']}")
        print(f"Scope: {selected_var['scope_description']}")
        print(f"Programme Impact: {selected_var['programme_impact']}")
        
        # Show cost breakdown
        labour_list = selected_var.get('Labor', [])
        material_list = selected_var.get('Materials', [])
        labour_total = sum(item.get('hours', 0) * item.get('rate', 0) for item in labour_list)
        materials_total = sum(item.get('quantity', 0) * item.get('unit_cost', 0) for item in material_list)
        
        if labour_list or material_list:
            print(f"\n--- COST BREAKDOWN ---")
            if labour_list:
                print(f"Labour ({len(labour_list)} items): ${labour_total:,.2f}")
            if material_list:
                print(f"Materials ({len(material_list)} items): ${materials_total:,.2f}")
            print(f"Total: ${labour_total + materials_total:,.2f}")
        
        print("\n1. Change Status")
        print("2. View Full Details")
        print("3. Back")
        
        action = input("Select: ").strip()
        
        if action == '1':
            status_map = {
                "1": "Draft",
                "2": "Proposed",
                "3": "Accepted",
                "4": "Rejected",
                "5": "Under Negotiation",
                "6": "Claimed"
            }
            print("\n1. Draft")
            print("2. Proposed")
            print("3. Accepted")
            print("4. Rejected")
            print("5. Under Negotiation")
            print("6. Claimed")

            status_choice = input("Select new status: ").strip()
            new_status = status_map.get(status_choice)

            if new_status:
                success, msg = storage.update_variation_status(selected_var['id'], new_status, current_user)
                print(f">> {msg}")
        
        elif action == '2':
            print("\n--- FULL DETAILS ---")
            if labour_list:
                print("\nLabour:")
                for item in labour_list:
                    print(f"  - {item.get('role', 'Unknown')}: {item.get('hours', 0)} hrs @ ${item.get('rate', 0):.2f} = ${item.get('hours', 0) * item.get('rate', 0):,.2f}")
            if material_list:
                print("\nMaterials:")
                for item in material_list:
                    print(f"  - {item.get('name', 'Unknown')}: {item.get('quantity', 0)} @ ${item.get('unit_cost', 0):.2f} = ${item.get('quantity', 0) * item.get('unit_cost', 0):,.2f}")
            input("\nPress Enter to continue...")