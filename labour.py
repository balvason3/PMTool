# --- PMTool: LABOUR MODULE ---

def get_labour_inputs():
    """Handles the loop to collect baseline estimates."""
    items = []
    print("\n--- LABOUR ESTIMATE (Baseline) ---")
    while True:
        role = input("Role (PM/Trade/Admin) or 'done': ").strip().title()
        if role.lower() == 'done': break
        try:
            hrs = float(input(f"  Estimated Hours for {role}: "))
            rate = float(input(f"  Hourly Rate for {role} ($): "))
            items.append({
                "role": role, 
                "estimated_hours": hrs, 
                "actual_hours": 0.0, # Initial baseline starts at 0
                "rate": rate
            })
        except ValueError:
            print("  !! Invalid number. Please retry.")
    return items

def calculate_labour_total(labour_list):
    """Calculates the dollar value of the baseline estimate."""
    return sum(l['estimated_hours'] * l['rate'] for l in labour_list)

def get_burn_report(labour_list):
    """Calculates variance between estimate and actuals."""
    report = []
    for l in labour_list:
        remaining = l['estimated_hours'] - l['actual_hours']
        status = "On Track" if remaining >= 0 else "OVER BUDGET"
        report.append({
            "role": l['role'],
            "remaining": remaining,
            "status": status
        })
    return report