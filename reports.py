# --- PMTool: REPORTS MODULE ---

def print_project_dashboard(selected):
    """Handles the UI display for a project's financial health."""
    print("\n" + "="*105)
    print(f"JOB NO:  {selected.get('Project_ID', 'N/A')} | STATUS: {selected.get('Status', 'Active').upper()}")
    print(f"PROJECT: {selected['Project'].upper()} | DATE: {selected.get('Timestamp', 'N/A')}")
    print(f"CLIENT:  {selected.get('Client', 'TBA')} | DUE: {selected.get('Target_Date', 'TBA')}")
    print(f"SCOPE:   {selected.get('Scope', 'N/A')}")
    print("-" * 105)
    
    # --- DETAILED LABOR TRACKER ---
    # Total width: 17+3+7+3+5+3+7+3+10+3+8+3+10+3+10+3+10 = 105
    print(f"{'Role':<17} | {'Orig Hr':>7} | {'Used':>5} | {'Rem Hr':>7} | {'Est Cost':>10} | {'Markup %':>8} | {'Est Sell':>10} | {'Rem Cost':>10} | {'Var Cost':>10}")
    print("-" * 105)
    
    labor_data = selected.get('Labor', [])
    total_orig_lab_val = total_sell_lab_val = total_rem_lab_val = total_var_lab_val = 0

    for l in labor_data:
        orig = l.get('estimated_hours', l.get('hours', 0))
        used = l.get('actual_hours', 0)
        rate = l.get('rate', 0)
        markup_val = l.get('markup_percent', 0.0)
        
        role_label = l['role'][:13] + " (V)" if l.get('variation') else l['role'][:17]
        
        orig_cost = orig * rate
        est_sell = orig_cost * (1 + (markup_val / 100))
        rem_hrs = orig - used
        rem_cost = max(0, rem_hrs * rate)
        var_cost = (used - orig) * rate if used > orig else 0.0
        
        total_orig_lab_val += orig_cost
        total_sell_lab_val += est_sell
        total_rem_lab_val += rem_cost
        total_var_lab_val += var_cost

        est_cost_str = f"${orig_cost:,.2f}"
        sell_str = f"${est_sell:,.2f}"
        rem_str = f"${rem_cost:,.2f}"
        var_str = f"${var_cost:,.2f}"
        markup_str = f"{markup_val:.1f}%"

        print(f"{role_label:<17} | {orig:>7.1f} | {used:>5.1f} | {rem_hrs:>7.1f} | {est_cost_str:>10} | {markup_str:>8} | {sell_str:>10} | {rem_str:>10} | {var_str:>10}")
    
    print("-" * 105)
    print(f"{'LABOR TOTALS':<17} | {'':>7} | {'':>5} | {'':>7} | {f'${total_orig_lab_val:,.2f}':>10} | {'':>8} | {f'${total_sell_lab_val:,.2f}':>10} | {f'${total_rem_lab_val:,.2f}':>10} | {f'${total_var_lab_val:,.2f}':>10}")
    
    # --- DETAILED MATERIALS TRACKER ---
    # Total width: 32+3+10+3+10+3+8+3+10+3+10+3+10 = 105
    print("\n" + f"{'Material Item':<32} | {'Est Cost':>10} | {'Spent':>10} | {'Markup %':>8} | {'Est Sell':>10} | {'Rem Cost':>10} | {'Var Cost':>10}")
    print("-" * 105)
    
    mats_data = selected.get('Materials', [])
    total_orig_mat_val = total_sell_mat_val = total_rem_mat_val = total_var_mat_val = 0
    
    for m in mats_data:
        orig_cost = m.get('estimated_cost', m.get('price', 0))
        spent = m.get('actual_cost', 0)
        markup_val = m.get('markup_percent', 0.0)
        
        proc_status = m.get('procurement_status', 'Pending')
        status_tag = ""
        if proc_status == 'Ready to Order':
            status_tag = "[RTO] "
        elif proc_status == 'Received':
            status_tag = "[RCVD] "
            
        base_name = status_tag + m['name']
        mat_label = base_name[:28] + " (V)" if m.get('variation') else base_name[:32]
        
        est_sell = orig_cost * (1 + (markup_val / 100))
        rem_cost = max(0, orig_cost - spent)
        var_cost = (spent - orig_cost) if spent > orig_cost else 0.0
        
        total_orig_mat_val += orig_cost
        total_sell_mat_val += est_sell
        total_rem_mat_val += rem_cost
        total_var_mat_val += var_cost
        
        orig_str = f"${orig_cost:,.2f}"
        spent_str = f"${spent:,.2f}"
        sell_str = f"${est_sell:,.2f}"
        rem_str = f"${rem_cost:,.2f}"
        var_str = f"${var_cost:,.2f}"
        markup_str = f"{markup_val:.1f}%"
        
        print(f"{mat_label:<32} | {orig_str:>10} | {spent_str:>10} | {markup_str:>8} | {sell_str:>10} | {rem_str:>10} | {var_str:>10}")
    
    print("-" * 105)
    print(f"{'MAT TOTALS':<32} | {f'${total_orig_mat_val:,.2f}':>10} | {f'${(sum(m.get('actual_cost', 0) for m in mats_data)):,.2f}':>10} | {'':>8} | {f'${total_sell_mat_val:,.2f}':>10} | {f'${total_rem_mat_val:,.2f}':>10} | {f'${total_var_mat_val:,.2f}':>10}")

    # --- GRAND SUMMARY ---
    print("=" * 105)
    total_orig_budget = total_orig_lab_val + total_orig_mat_val
    total_ex = selected.get('Total_Ex_GST', 0)
    total_markup = total_ex - total_orig_budget
    total_variance = total_var_lab_val + total_var_mat_val
    
    # Total width: 89 text + 3 spacer + 13 money = 105
    print(f"{'Base Budget (Raw Cost of Labour + Materials):':<89} | {f'${total_orig_budget:,.2f}':>13}")
    print(f"{'Total Markup (Profit Margin):':<89} | {f'${total_markup:,.2f}':>13}")
    print(f"{'Total Excl. GST (Sell Price):':<89} | {f'${total_ex:,.2f}':>13}")
    print(f"{'GST (10%):':<89} | {f'${selected.get('GST', 0):,.2f}':>13}")
    
    if total_variance > 0:
        print("-" * 105)
        print(f"{'TOTAL OVERRUN (NON-BILLABLE LOSS):':<89} | {f'${total_variance:,.2f}':>13}")
    print("-" * 105)
    print(f"{'GRAND TOTAL (Inc GST & Markup):':<89} | {f'${selected.get('Total_Inc_GST', 0):,.2f}':>13}")
    print("=" * 105)
    
    # --- PRINT NOTES LOG ---
    project_notes = selected.get("Notes", [])
    if project_notes:
        print("\n--- ACTIVITY LOG & NOTES ---")
        for note in project_notes:
            print(f"[{note['timestamp']}] {note['text']}")
        print("-" * 105)