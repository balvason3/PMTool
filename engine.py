# --- PMTool: ENGINE MODULE ---
# This file contains the logic and math only. 
# No menus or inputs are allowed here.

def calculate_gst(amount):
    """
    Calculates 10% GST based on Australian standards.
    Input: Numerical amount
    Output: Dictionary with GST value and total including GST
    """
    gst_amount = amount * 0.10
    return {
        "gst_value": gst_amount,
        "total_inc_gst": amount + gst_amount
    }

    def calculate_totals(labor_hours, hourly_rate, items_list, contingency_rate=0.15):
    """
    items_list should be a list of dictionaries: 
    [{'name': 'Timber', 'price': 100}, {'name': 'Glue', 'price': 20}]
    """
    # Sum up all materials from the list
    materials_subtotal = sum(item['price'] for item in items_list)
    
    labor_subtotal = labor_hours * hourly_rate
    base_total = labor_subtotal + materials_subtotal
    
    contingency = base_total * contingency_rate
    total_ex_gst = base_total + contingency
    
    return {
        "labor_total": labor_total,
        "materials_total": materials_subtotal,
        "contingency": contingency,
        "total_ex": total_ex_gst
    }