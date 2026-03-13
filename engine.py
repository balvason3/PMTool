# --- PMTool: ENGINE MODULE ---

def calculate_gst(amount):
    """Calculates 10% GST and returns the GST value and grand total."""
    gst_amount = amount * 0.10
    return {
        "gst_value": gst_amount,
        "total_inc_gst": amount + gst_amount
    }

def calculate_totals(labor_list, materials_list, contingency_rate=0.15):
    """
    Combines labor baseline and materials to find the project total.
    labor_list: [{'role': 'PM', 'estimated_hours': 10, 'rate': 100, ...}]
    materials_list: [{'name': 'Timber', 'price': 500}]
    """
    
    # 1. Sum Labor (using estimated_hours for the quote/baseline)
    labor_subtotal = sum(l['estimated_hours'] * l['rate'] for l in labor_list)
    
    # 2. Sum Materials
    materials_subtotal = sum(m['price'] for m in materials_list)
    
    # 3. Calculate Base and Contingency
    base_total = labor_subtotal + materials_subtotal
    contingency = base_total * contingency_rate
    total_ex_gst = base_total + contingency
    
    return {
        "labor_total": labor_subtotal,
        "materials_total": materials_subtotal,
        "contingency": contingency,
        "total_ex": total_ex_gst
    }