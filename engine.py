# --- PMTool: ENGINE MODULE ---
import settings

def calculate_gst(amount):
    config = settings.load_settings()
    gst_amount = amount * config['gst_rate']
    return {
        "gst_value": gst_amount,
        "total_inc_gst": amount + gst_amount
    }

def calculate_totals(labor_list, materials_list):
    config = settings.load_settings()
    default_markup = config['markup_rate']
        
    labor_cost = 0
    labor_sell = 0
    for item in labor_list:
        cost = item['estimated_hours'] * item['rate']
        labor_cost += cost
        # Pull the item's specific markup, or fallback to default
        markup_pct = item.get('markup_percent', default_markup * 100) / 100
        labor_sell += cost * (1 + markup_pct)
        
    mats_cost = 0
    mats_sell = 0
    for item in materials_list:
        cost = item.get('estimated_cost', item.get('price', 0))
        mats_cost += cost
        markup_pct = item.get('markup_percent', default_markup * 100) / 100
        mats_sell += cost * (1 + markup_pct)

    base_cost = labor_cost + mats_cost
    total_ex_gst = labor_sell + mats_sell
    total_markup = total_ex_gst - base_cost
    
    return {
        "labor_total": labor_cost,
        "materials_total": mats_cost,
        "markup": total_markup,
        "total_ex": total_ex_gst
    }