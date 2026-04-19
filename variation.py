# --- BEDROCK: VARIATIONS MODULE ---
import storage

def variations_menu(selected, current_user):
    """Shows all variations for a project and provides options to add or update."""
    while True:
        internal_id = selected.get('internal_id')
        display_id = selected.get('Project_ID') or selected.get('Quote_Number')
        project_name = selected.get('Project')

        variations = storage.get_variations_by_project(internal_id)

        print(f"\n--- VARIATIONS | {display_id} | {project_name} ---")
        print(f"{'Ref':<6} | {'Status':<15} | {'Reason':<20} | {'Cost Impact':>12} | {'Raised By':<15}")
        print("-" * 75)

        if not variations:
            print("No variations found for this project.")
        else:
            for v in variations:
                print(f"{v['reference']:<6} | {v['status']:<15} | {v['reason']:<20} | ${v['cost_impact']:>11,.2f} | {v['raised_by']:<15}")

        print("-" * 75)
        print("1. Add New Variation")
        print("2. Update Variation Status")
        print("0. Back")

        choice = input("\nSelect: ").strip()

        if choice == '1':
            add_variation_ui(selected, current_user)
        elif choice == '2':
            update_variation_ui(selected, current_user)
        elif choice == '0':
            break

def add_variation_ui(selected, current_user):
    """Collects inputs from PM and creates a new variation in Draft status."""
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
    print("1. Client Request")
    print("2. Latent Condition")
    print("3. Design Change")
    reason_choice = input("Select reason: ").strip()
    reason = reason_map.get(reason_choice, "Client Request")

    try:
        cost_impact = float(input("Cost impact $: "))
    except ValueError:
        print("!! Invalid amount.")
        return

    programme_impact = input("Programme impact (or leave blank): ").strip()

    ref = storage.save_variation(internal_id, current_user, scope, reason, cost_impact, programme_impact)
    print(f">> {ref} created successfully.")

def update_variation_ui(selected, current_user):
    """Lets PM pick a variation and update its status."""
    internal_id = selected.get('internal_id')
    variations = storage.get_variations_by_project(internal_id)

    if not variations:
        print("!! No variations found for this project.")
        return

    print("\n--- UPDATE VARIATION STATUS ---")
    for v in variations:
        print(f"{v['reference']} | {v['status']} | {v['scope_description'][:40]}")

    ref_choice = input("\nEnter variation reference (e.g. V1): ").strip().upper()

    selected_var = next((v for v in variations if v['reference'] == ref_choice), None)
    if not selected_var:
        print("!! Variation not found.")
        return

    status_map = {
        "1": "Draft",
        "2": "Proposed",
        "3": "Accepted",
        "4": "Rejected",
        "5": "Under Negotiation",
        "6": "Claimed"
    }
    print("\n1. Draft")
    print("2. Proposed (Letter Sent)")
    print("3. Accepted")
    print("4. Rejected")
    print("5. Under Negotiation")
    print("6. Claimed")

    status_choice = input("Select new status: ").strip()
    new_status = status_map.get(status_choice)

    if not new_status:
        print("!! Invalid selection.")
        return

    success, msg = storage.update_variation_status(selected_var['id'], new_status, current_user)
    print(f">> {msg}")