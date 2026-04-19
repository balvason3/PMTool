# --- PMTool: VARIATION PDF GENERATOR MODULE ---
import storage
import settings
import os
import sys
from datetime import datetime
from xhtml2pdf import pisa

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def generate_variation_pdf_ui(project, current_user):
    """Generates a PDF for a selected variation."""
    internal_id = project.get('internal_id')
    variations = storage.get_variations_by_project(internal_id)

    if not variations:
        print("\n!! No variations found for this project.")
        input("Press Enter to return...")
        return

    # Select variation
    print("\n--- GENERATE VARIATION PDF ---")
    for i, var in enumerate(variations):
        print(f"{i+1}. {var['reference']} | {var['status']} | Cost: ${var['cost_impact']:,.2f}")
    
    choice = input("\nSelect Variation # (0 to cancel): ").strip()
    if not (choice.isdigit() and 0 < int(choice) <= len(variations)):
        return

    selected_var = variations[int(choice)-1]
    
    # Load Settings
    config = settings.load_settings()
    my_company = config.get('company_details', {})
    
    # Build HTML
    html_content = build_variation_html(project, selected_var, my_company)
    
    # Generate PDF
    EXPORT_DIR = 'exports'
    os.makedirs(EXPORT_DIR, exist_ok=True)
    filename = f"VARIATION_{project.get('Quote_Number') or project.get('Project_ID')}_{selected_var['reference']}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)
    
    with open(filepath, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)

    if pisa_status.err:
        print("!! Error generating PDF.")
    else:
        print(f"\n>> SUCCESS: PDF saved as '{filepath}'")
    
    input("\nPress Enter to return...")


def build_variation_html(project, variation, my_company):
    """Builds the HTML content for a variation PDF (1-pager)."""
    
    # Extract data
    project_id = project.get('Project_ID') or project.get('Quote_Number')
    project_name = project.get('Project', 'Untitled')
    client = project.get('Client', 'TBA')
    var_ref = variation.get('reference', 'N/A')
    var_status = variation.get('status', 'Draft')
    var_scope = variation.get('scope_description', 'N/A')
    var_reason = variation.get('reason', 'N/A')
    cost_impact = variation.get('cost_impact', 0.0)
    programme_impact = variation.get('programme_impact', 'N/A')
    raised_by = variation.get('raised_by', 'N/A')
    raised_date = variation.get('raised_date', 'N/A')
    
    labor_list = variation.get('Labor', [])
    material_list = variation.get('Materials', [])
    
    date_str = datetime.now().strftime('%d-%m-%Y')
    
    # Build labour rows
    labour_rows = ""
    labour_total = 0.0
    for labour_item in labor_list:
        role = labour_item.get('role', 'Unknown')
        hours = labour_item.get('hours', 0)
        rate = labour_item.get('rate', 0)
        subtotal = hours * rate
        labour_total += subtotal
        labour_rows += f"""
            <tr>
                <td>{role}</td>
                <td style="text-align: center;">{hours:.2f}</td>
                <td style="text-align: right;">${rate:,.2f}</td>
                <td style="text-align: right;">${subtotal:,.2f}</td>
            </tr>
        """
    
    # Build materials rows
    materials_rows = ""
    materials_total = 0.0
    for material_item in material_list:
        name = material_item.get('name', 'Unknown')
        quantity = material_item.get('quantity', 1)
        unit_cost = material_item.get('unit_cost', 0)
        subtotal = quantity * unit_cost
        materials_total += subtotal
        materials_rows += f"""
            <tr>
                <td>{name}</td>
                <td style="text-align: center;">{quantity:.2f}</td>
                <td style="text-align: right;">${unit_cost:,.2f}</td>
                <td style="text-align: right;">${subtotal:,.2f}</td>
            </tr>
        """
    
    # Calculate total if not already set
    calculated_total = labour_total + materials_total
    if calculated_total == 0 and cost_impact > 0:
        calculated_total = cost_impact
    
    # Build HTML (1 page format)
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        @page {{ size: A4 portrait; margin: 1cm; }}
        body {{ font-family: Helvetica, sans-serif; font-size: 9pt; color: #333; }}
        .header {{ width: 100%; margin-bottom: 10px; border-bottom: 2px solid #2c3e50; padding-bottom: 8px; }}
        .title {{ font-size: 16pt; font-weight: bold; color: #2c3e50; }}
        .project-info {{ font-size: 8pt; color: #666; margin-top: 3px; }}
        .var-title {{ font-size: 13pt; font-weight: bold; color: #2c3e50; margin: 8px 0 5px 0; }}
        .details {{ font-size: 8pt; margin: 5px 0; }}
        .details-bold {{ font-weight: bold; }}
        .scope-box {{ background-color: #f9f9f9; border: 1px solid #ddd; padding: 6px; margin: 5px 0; font-size: 8pt; }}
        .items-table {{ width: 100%; border-collapse: collapse; margin: 5px 0; font-size: 8pt; }}
        .items-table th {{ background-color: #2c3e50; color: white; padding: 4px; text-align: left; }}
        .items-table td {{ padding: 3px 4px; border-bottom: 1px solid #ddd; }}
        .subtotal-row {{ background-color: #ecf0f1; font-weight: bold; }}
        .total-box {{ font-size: 10pt; font-weight: bold; color: #2c3e50; margin: 8px 0; padding: 6px; border: 2px solid #2c3e50; text-align: right; }}
        .footer {{ margin-top: 8px; font-size: 7pt; color: #999; border-top: 1px solid #ddd; padding-top: 5px; text-align: center; }}
    </style>
</head>
<body>
    <table style="width: 100%; margin-bottom: 2px;">
        <tr>
            <td style="width: 50%;">
                <div class="title">{my_company.get('name', 'YOUR COMPANY')}</div>
                <div class="project-info">ABN: {my_company.get('abn', 'YOUR ABN')}</div>
            </td>
            <td style="width: 50%; text-align: right; vertical-align: top;">
                <div style="font-size: 14pt; font-weight: bold; color: #2c3e50;">VARIATION</div>
                <div style="font-size: 9pt; color: #666;">{var_ref} | {var_status}</div>
            </td>
        </tr>
    </table>

    <div class="details">
        <span class="details-bold">Project:</span> {project_name} ({project_id}) | <span class="details-bold">Client:</span> {client}
    </div>
    <div class="details">
        <span class="details-bold">Raised:</span> {raised_date} by {raised_by} | <span class="details-bold">Reason:</span> {var_reason}
    </div>

    <div class="var-title">SCOPE OF VARIATION</div>
    <div class="scope-box">{var_scope}</div>

    <div class="var-title">COST BREAKDOWN</div>
    
    {"<table class=\"items-table\"><thead><tr><th style=\"width: 40%;\">Role / Description</th><th style=\"width: 20%; text-align: center;\">Qty/Hours</th><th style=\"width: 20%; text-align: right;\">Rate</th><th style=\"width: 20%; text-align: right;\">Subtotal</th></tr></thead><tbody>" + labour_rows + ("<tr class=\"subtotal-row\"><td colspan=\"3\" style=\"text-align: right;\">Labour:</td><td style=\"text-align: right;\">${" + f"{labour_total:,.2f}" + "}</td></tr>" if labour_rows else "") + "</tbody></table>" if labour_rows else ""}
    
    {"<table class=\"items-table\"><thead><tr><th style=\"width: 40%;\">Description</th><th style=\"width: 20%; text-align: center;\">Qty</th><th style=\"width: 20%; text-align: right;\">Unit Cost</th><th style=\"width: 20%; text-align: right;\">Subtotal</th></tr></thead><tbody>" + materials_rows + ("<tr class=\"subtotal-row\"><td colspan=\"3\" style=\"text-align: right;\">Materials:</td><td style=\"text-align: right;\">${" + f"{materials_total:,.2f}" + "}</td></tr>" if materials_rows else "") + "</tbody></table>" if materials_rows else ""}

    <div class="total-box">
        TOTAL VARIATION COST: ${calculated_total:,.2f}
    </div>

    <div class="details">
        <span class="details-bold">Programme Impact:</span> {programme_impact}
    </div>

    <div class="footer">
        Generated {date_str} by PMTool | This variation is subject to approval. Status: {var_status}
    </div>
</body>
</html>
"""
    
    return html_content
