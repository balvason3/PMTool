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

def calculate_totals(labor_hours, hourly_rate, materials_cost, contingency_rate=0.15):
    """
    Calculates project subtotal and contingency buffer.
    All calculations are Ex-GST.
    """
    subtotal_ex_gst = (labor_hours * hourly_rate) + materials_cost
    contingency_ex_gst = subtotal_ex_gst * contingency_rate
    total_ex_gst = subtotal_ex_gst + contingency_ex_gst
    
    return {
        "total_ex": total_ex_gst,
        "contingency": contingency_ex_gst,
        "base_subtotal": subtotal_ex_gst
    }