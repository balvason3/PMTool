# --- PMTool: ENGINE MODULE ---

def calculate_gst(amount):
    gst_amount = amount * 0.10
    return {
        "gst_value": gst_amount,
        "total_inc_gst": amount + gst_amount
    }

def calculate_totals(labor_list, materials_list, contingency_rate=0.15):
    # Sum Labor baseline (estimated_hours * rate)
    labor_subtotal = sum(item['estimated_hours'] * item['rate'] for item in labor_list)
    
    # Sum Materials baseline (using the new estimated_cost key)
    materials_subtotal = sum(item.get('estimated_cost', item.get('price', 0)) for item in materials_list)
    
    base_total = labor_subtotal + materials_subtotal
    contingency = base_total * contingency_rate
    total_ex_gst = base_total + contingency
    
    return {
        "labor_total": labor_subtotal,
        "materials_total": materials_subtotal,
        "contingency": contingency,
        "total_ex": total_ex_gst
    }