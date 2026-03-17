# --- PMTool: REPORTS MODULE ---

def print_project_dashboard(selected):
    """Handles the UI display for a project's financial health."""
    print("\n" + "="*75)
    print(f"JOB NO:  {selected.get('Project_ID', 'N/A')} | STATUS: {selected.get('Status', 'Active').upper()}")
    print(f"PROJECT: {selected['Project'].upper()} | DATE: {selected.get('Timestamp', 'N/A')}")
    print(f"SCOPE:   {selected.get('Scope', 'N/A')}")
    print("-" * 75)
    
    # --- DETAILED LABOR TRACKER ---
    print(f"{'Role':<14} | {'Orig Hr':>7} | {'Used':>5} | {'Rem Hr':>6} | {'Rem $':>11} | {'Var $':>10}")
    print("-" * 75)
    
    labor_data = selected.get('Labor', [])
    total_orig_lab_val = total_rem_lab_val = total_var_lab_val = 0

    for l in labor_data:
        orig = l.get('estimated_hours', l.get('hours', 0))
        used = l.get('actual_hours', 0)
        rate = l.get('rate', 0)
        
        # Add a (V) tag if this was a variation added later
        role_label = l['role'][:10] + " (V)" if l.get('variation') else l['role'][:14]
        
        rem_hrs = orig - used
        rem_cost = max(0, rem_hrs * rate)
        var_cost = (used - orig) * rate if used > orig else 0.0
        
        total_orig_lab_val += (orig * rate)
        total_rem_lab_val += rem_cost
        total_var_lab_val += var_cost

        print(f"{role_label:<14} | {orig:>7.1f} | {used:>5.1f} | {rem_hrs:>6.1f} | ${rem_cost:>10,.2f} | ${var_cost:>9,.2f}")
    
    print("-" * 75)
    print(f"{'LABOR TOTALS':<14} | {'':>7} | {'':>5} | {'':>6} | ${total_rem_lab_val:>10,.2f} | ${total_var_lab_val:>9,.2f}")
    
    # --- DETAILED MATERIALS TRACKER ---
    print("\n" + f"{'Material Item':<29} | {'Orig $':>10} | {'Spent $':>9} | {'Rem $':>9} | {'Var $':>9}")
    print("-" * 75)
    
    mats_data = selected.get('Materials', [])
    total_orig_mat_val = total_rem_mat_val = total_var_mat_val = 0
    
    for m in mats_data:
        orig_cost = m.get('estimated_cost', m.get('price', 0))
        spent = m.get('actual_cost', 0)
        
        mat_label = m['name'][:25] + " (V)" if m.get('variation') else m['name'][:29]
        
        rem_cost = max(0, orig_cost - spent)
        var_cost = (spent - orig_cost) if spent > orig_cost else 0.0
        
        total_orig_mat_val += orig_cost
        total_rem_mat_val += rem_cost
        total_var_mat_val += var_cost
        
        print(f"{mat_label:<29} | ${orig_cost:>8,.2f} | ${spent:>7,.2f} | ${rem_cost:>7,.2f} | ${var_cost:>8,.2f}")
    
    print("-" * 75)
    print(f"{'MAT TOTALS':<29} | {'':>10} | {'':>9} | ${total_rem_mat_val:>7,.2f} | ${total_var_mat_val:>8,.2f}")

    # --- GRAND SUMMARY ---
    print("=" * 75)
    total_orig_budget = total_orig_lab_val + total_orig_mat_val
    total_ex = selected.get('Total_Ex_GST', 0)
    contingency = total_ex - total_orig_budget
    total_variance = total_var_lab_val + total_var_mat_val
    
    print(f"{'Base Budget (Labour + Materials):':<58} | ${total_orig_budget:>11,.2f}")
    print(f"{'Contingency (15%):':<58} | ${contingency:>11,.2f}")
    print(f"{'Total Excl. GST:':<58} | ${total_ex:>11,.2f}")
    print(f"{'GST (10%):':<58} | ${selected.get('GST', 0):>11,.2f}")
    
    if total_variance > 0:
        print("-" * 75)
        print(f"{'TOTAL OVERRUN (NON-BILLABLE LOSS):':<58} | ${total_variance:>11,.2f}")
    print("-" * 75)
    print(f"{'GRAND TOTAL (Inc GST & Contingency):':<58} | ${selected.get('Total_Inc_GST', 0):11,.2f}")
    print("=" * 75)