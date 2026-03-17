# --- PMTool: REPORTS MODULE ---

def print_project_dashboard(selected):
    """Handles the UI display for a project's financial health."""
    print("\n" + "="*75)
    print(f"JOB NO:  {selected.get('Project_ID', 'N/A')}")
    print(f"PROJECT: {selected['Project'].upper()} | DATE: {selected.get('Timestamp', 'N/A')}")
    print(f"SCOPE:   {selected.get('Scope', 'N/A')}")
    print("-" * 75)
    
    # --- DETAILED LABOR TRACKER ---
    print(f"{'Role':<12} | {'Orig Hr':>7} | {'Used':>5} | {'Rem Hr':>6} | {'Rem $':>12} | {'Var $':>10}")
    print("-" * 75)
    
    labor_data = selected.get('Labor', [])
    total_orig_lab_val = total_rem_lab_val = total_var_lab_val = 0

    for l in labor_data:
        orig = l.get('estimated_hours', l.get('hours', 0))
        used = l.get('actual_hours', 0)
        rate = l.get('rate', 0)
        
        rem_hrs = orig - used
        rem_cost = max(0, rem_hrs * rate)
        var_cost = (used - orig) * rate if used > orig else 0.0
        
        total_orig_lab_val += (orig * rate)
        total_rem_lab_val += rem_cost
        total_var_lab_val += var_cost

        print(f"{l['role']:<12} | {orig:>7.1f} | {used:>5.1f} | {rem_hrs:>6.1f} | ${rem_cost:>11,.2f} | ${var_cost:>9,.2f}")
    
    print("-" * 75)
    print(f"{'LABOR TOTALS':<12} | {'':>7} | {'':>5} | {'':>6} | ${total_rem_lab_val:>11,.2f} | ${total_var_lab_val:>9,.2f}")
    
    # --- DETAILED MATERIALS TRACKER ---
    print("\n" + f"{'Material Item':<27} | {'Orig $':>10} | {'Spent $':>10} | {'Rem $':>10} | {'Var $':>9}")
    print("-" * 75)
    
    mats_data = selected.get('Materials', [])
    total_orig_mat_val = total_rem_mat_val = total_var_mat_val = 0
    
    for m in mats_data:
        orig_cost = m.get('estimated_cost', m.get('price', 0))
        spent = m.get('actual_cost', 0)
        
        rem_cost = max(0, orig_cost - spent)
        var_cost = (spent - orig_cost) if spent > orig_cost else 0.0
        
        total_orig_mat_val += orig_cost
        total_rem_mat_val += rem_cost
        total_var_mat_val += var_cost
        
        print(f"{m['name']:<27} | ${orig_cost:>8,.2f} | ${spent:>8,.2f} | ${rem_cost:>8,.2f} | ${var_cost:>8,.2f}")
    
    print("-" * 75)
    print(f"{'MAT TOTALS':<27} | {'':>10} | {'':>10} | ${total_rem_mat_val:>8,.2f} | ${total_var_mat_val:>8,.2f}")

    # --- GRAND SUMMARY ---
    print("=" * 75)
    total_orig_budget = total_orig_lab_val + total_orig_mat_val
    total_variance = total_var_lab_val + total_var_mat_val
    
    print(f"{'Original Base Budget (Lab + Mat):':<58} | ${total_orig_budget:>11,.2f}")
    if total_variance > 0:
        print(f"{'TOTAL OVERRUN (LOSS):':<58} | ${total_variance:>11,.2f}")
    print("-" * 75)
    print(f"{'GRAND TOTAL (Inc GST & Contingency):':<58} | ${selected.get('Total_Inc_GST', 0):11,.2f}")
    print("=" * 75)