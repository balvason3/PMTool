# --- PMTool: ESTIMATE PDF GENERATOR MODULE ---
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

def generate_estimate_pdf_ui():
    """Generates a PDF Estimate/Quote using the HTML template."""
    logs = storage.get_all_history()
    estimate_items = {}
    
    # 1. Gather Draft and Quoted estimates
    for p_idx, project in enumerate(logs):
        if project.get('Status') in ['Draft', 'Quoted']:
            quote_num = project.get('Quote_Number', 'N/A')
            estimate_items[quote_num] = (p_idx, project)

    if not estimate_items:
        print("\n!! No estimates currently in Draft or Quoted status.")
        input("Press Enter to return...")
        return

    # 2. Select Estimate
    print("\n--- GENERATE ESTIMATE PDF ---")
    estimates_list = list(estimate_items.keys())
    for i, quote_num in enumerate(estimates_list):
        proj_name = estimate_items[quote_num][1].get('Project', 'Unknown')
        print(f"{i+1}. {quote_num} - {proj_name}")
    
    choice = input("\nSelect Estimate # to generate PDF (0 to cancel): ").strip()
    if not (choice.isdigit() and 0 < int(choice) <= len(estimates_list)):
        return

    selected_quote = estimates_list[int(choice)-1]
    p_idx, project = estimate_items[selected_quote]
    
    # 3. Load Settings
    config = settings.load_settings()
    my_company = config.get('company_details', {})
    
    # 4. Create HTML Content
    html_content = build_estimate_html(project, my_company)
    
    # 5. Generate the PDF
    EXPORT_DIR = 'exports'
    os.makedirs(EXPORT_DIR, exist_ok=True)
    filename = f"ESTIMATE_{selected_quote}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)
    
    with open(filepath, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)

    if pisa_status.err:
        print("!! Error generating PDF.")
    else:
        print(f"\n>> SUCCESS: PDF saved as '{filepath}'")
    
    input("\nPress Enter to return...")


def build_estimate_html(project, my_company):
    """Builds the HTML content for the estimate PDF."""
    
    # Extract project data
    quote_num = project.get('Quote_Number', 'N/A')
    project_name = project.get('Project', 'Untitled Project')
    client = project.get('Client', 'TBA')
    target_date = project.get('Target_Date', 'TBA')
    scope = project.get('Scope', 'N/A')
    method = project.get('Method', 'N/A')
    version = project.get('Version', '1.0')
    
    labor_list = project.get('Labor', [])
    material_list = project.get('Materials', [])
    
    total_ex_gst = project.get('Total_Ex_GST', 0.0)
    gst_value = project.get('GST', 0.0)
    total_inc_gst = project.get('Total_Inc_GST', 0.0)
    
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
    
    # Build HTML
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        @page {{ size: A4 portrait; margin: 1.5cm; }}
        body {{ font-family: Helvetica, sans-serif; font-size: 10pt; color: #333; }}
        .header-table {{ width: 100%; margin-bottom: 20px; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }}
        .title {{ font-size: 20pt; font-weight: bold; color: #2c3e50; text-align: center; margin: 20px 0; }}
        .subtitle {{ font-size: 12pt; font-weight: bold; color: #2c3e50; margin: 15px 0 10px 0; }}
        .details-table {{ width: 100%; margin-bottom: 20px; }}
        .details-table td {{ vertical-align: top; padding-right: 20px; font-size: 9pt; }}
        .box-title {{ font-weight: bold; font-size: 11pt; color: #2c3e50; margin-bottom: 5px; border-bottom: 1px solid #ddd;}}
        .items-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        .items-table th {{ background-color: #2c3e50; color: white; padding: 8px; text-align: left; font-size: 9pt; }}
        .items-table td {{ padding: 6px 8px; border-bottom: 1px solid #ddd; font-size: 9pt; }}
        .section-header {{ background-color: #ecf0f1; font-weight: bold; font-size: 10pt; padding: 8px; margin-top: 15px; margin-bottom: 8px; border-left: 3px solid #2c3e50; }}
        .scope-box {{ background-color: #f9f9f9; border: 1px solid #ddd; padding: 10px; margin: 10px 0; font-size: 9pt; }}
        .totals-section {{ margin-top: 20px; text-align: right; }}
        .total-row {{ font-weight: bold; font-size: 11pt; margin: 5px 0; }}
        .footer {{ margin-top: 30px; font-size: 8pt; color: #7f8c8d; border-top: 1px solid #ddd; padding-top: 10px; text-align: center; }}
    </style>
</head>
<body>
    <table class="header-table">
        <tr>
            <td style="width: 50%; font-size: 14pt; font-weight: bold; color: #2c3e50;">
                {my_company.get('name', 'YOUR COMPANY')}
            </td>
            <td style="width: 50%; text-align: right;">
                <div style="font-size: 16pt; font-weight: bold; color: #2c3e50;">ESTIMATE/QUOTE</div>
                <div style="font-size: 9pt; color: #666;">Version {version}</div>
            </td>
        </tr>
    </table>

    <table class="details-table">
        <tr>
            <td style="width: 33%;">
                <div class="box-title">FROM</div>
                <strong>{my_company.get('name', 'YOUR COMPANY NAME')}</strong><br>
                ABN: {my_company.get('abn', 'YOUR ABN')}<br>
                {my_company.get('address', 'YOUR ADDRESS')}<br>
                Ph: {my_company.get('phone', 'YOUR PHONE')}<br>
                Email: {my_company.get('email', 'YOUR EMAIL')}
            </td>
            <td style="width: 33%;">
                <div class="box-title">TO</div>
                <strong>{client}</strong><br>
                <em>(Client details as per engagement)</em>
            </td>
            <td style="width: 33%;">
                <div class="box-title">ESTIMATE DETAILS</div>
                <strong>Quote #:</strong> {quote_num}<br>
                <strong>Date:</strong> {date_str}<br>
                <strong>Target Completion:</strong> {target_date}<br>
                <strong>Version:</strong> {version}
            </td>
        </tr>
    </table>

    <div style="margin: 20px 0;">
        <div style="font-size: 12pt; font-weight: bold; color: #2c3e50; margin-bottom: 10px;">PROJECT: {project_name}</div>
    </div>

    <div class="section-header">SCOPE OF WORK</div>
    <div class="scope-box">
        {scope}
    </div>

    <div class="section-header">METHOD / APPROACH</div>
    <div class="scope-box">
        {method}
    </div>

    <div class="section-header">LABOUR</div>
    <table class="items-table">
        <thead>
            <tr>
                <th style="width: 40%;">Role / Description</th>
                <th style="width: 20%; text-align: center;">Hours</th>
                <th style="width: 20%; text-align: right;">Rate (Ex GST)</th>
                <th style="width: 20%; text-align: right;">Subtotal (Ex GST)</th>
            </tr>
        </thead>
        <tbody>
            {labour_rows}
            <tr style="background-color: #ecf0f1; font-weight: bold;">
                <td colspan="3" style="text-align: right;">Labour Subtotal:</td>
                <td style="text-align: right;">${labour_total:,.2f}</td>
            </tr>
        </tbody>
    </table>

    <div class="section-header">MATERIALS & COMPONENTS</div>
    <table class="items-table">
        <thead>
            <tr>
                <th style="width: 40%;">Description</th>
                <th style="width: 20%; text-align: center;">Quantity</th>
                <th style="width: 20%; text-align: right;">Unit Cost (Ex GST)</th>
                <th style="width: 20%; text-align: right;">Subtotal (Ex GST)</th>
            </tr>
        </thead>
        <tbody>
            {materials_rows}
            <tr style="background-color: #ecf0f1; font-weight: bold;">
                <td colspan="3" style="text-align: right;">Materials Subtotal:</td>
                <td style="text-align: right;">${materials_total:,.2f}</td>
            </tr>
        </tbody>
    </table>

    <div class="totals-section">
        <div class="total-row">Subtotal (Ex GST): <span style="font-weight: normal;">${total_ex_gst:,.2f}</span></div>
        <div class="total-row">GST (10%): <span style="font-weight: normal;">${gst_value:,.2f}</span></div>
        <div style="font-size: 13pt; font-weight: bold; color: #2c3e50; margin-top: 10px; padding-top: 10px; border-top: 2px solid #2c3e50;">
            TOTAL (Inc GST): ${total_inc_gst:,.2f}
        </div>
    </div>

    <div class="footer">
        This is an estimate provided on {{DATE}}. Please note this quote is valid for 30 days from the date above.
        <br>Terms and conditions apply. Generated by PMTool.
    </div>
</body>
</html>
"""
    
    return html_content
