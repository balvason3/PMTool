# --- PMTool: ENGINE MODULE ---
# This file contains the logic and math only. 
# No menus or inputs are allowed here.

def calculate_gst(amount):
    # Calculates 10% GST based on Australian standards.
    gst_amount = amount * 0.10
    return {
        "gst_value": gst_amount,
        "total_inc_gst": amount + gst_amount
    }

# This must be at the left margin!
def calculate_totals(labor_hours, hourly_rate, items_list, contingency_rate=0.15):
    # Sum up the 'price' field for every dictionary in the list
    materials_subtotal = sum(item['price'] for item in items_list)
    
    labor_subtotal = labor_hours * hourly_rate
    base_total = labor_subtotal + materials_subtotal
    
    contingency = base_total * contingency_rate
    total_ex_gst = base_total + contingency
    
    return {
        "labor_total": labor_subtotal,
        "materials_total": materials_subtotal,
        "contingency": contingency,
        "total_ex": total_ex_gst
    }
    
def calculate_totals(labor_items, materials_items, contingency_rate=0.15):
    """
    labor_items: [{'role': 'PM', 'hours': 10, 'rate': 100}, ...]
    materials_items: [{'name': 'Timber', 'price': 500}, ...]
    """
    # Sum up Labor
    labor_subtotal = sum(l['hours'] * l['rate'] for l in labor_items)
    
    # Sum up Materials
    materials_subtotal = sum(m['price'] for m in materials_items)
    
    base_total = labor_subtotal + materials_subtotal
    contingency = base_total * contingency_rate
    total_ex_gst = base_total + contingency
    
    return {
        "labor_total": labor_subtotal,
        "materials_total": materials_subtotal,
        "contingency": contingency,
        "total_ex": total_ex_gst
    }