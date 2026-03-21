# --- PMTool: PURCHASE ORDER GENERATOR MODULE ---
import storage
import supplier
import settings
from datetime import datetime
from xhtml2pdf import pisa

def generate_purchase_order_ui():
    """Generates a PDF Purchase Order using the HTML template."""
    logs = storage.get_all_history()
    rto_items = {}
    
    # 1. Gather RTO items and group by Supplier
    for p_idx, project in enumerate(logs):
        if project.get('Status') != 'Active': continue
        for m_idx, m in enumerate(project.get('Materials', [])):
            if m.get('procurement_status') == 'Ready to Order':
                sup = m.get('supplier', 'TBA')
                if sup not in rto_items: rto_items[sup] = []
                rto_items[sup].append((p_idx, m_idx, project.get('Project_ID', 'N/A'), m))

    if not rto_items:
        print("\n!! No items are currently tagged as 'Ready to Order'.")
        input("Press Enter to return...")
        return

    # 2. Select Supplier
    print("\n--- GENERATE PURCHASE ORDER ---")
    suppliers_list = list(rto_items.keys())
    for i, sup in enumerate(suppliers_list):
        print(f"{i+1}. {sup} ({len(rto_items[sup])} items waiting)")
    
    choice = input("\nSelect Supplier # to generate PO (0 to cancel): ").strip()
    if not (choice.isdigit() and 0 < int(choice) <= len(suppliers_list)):
        return

    selected_sup = suppliers_list[int(choice)-1]
    items_to_order = rto_items[selected_sup]
    
    # --- NEW: Ask for the Quote Number ---
    quote_ref = input(f"Enter {selected_sup} Quote Number (Press Enter to skip): ").strip()

    # 3. Load Data and Template
    sup_db = supplier.load_suppliers()
    sup_details = next((s for s in sup_db if s.get('name') == selected_sup), {})
    
    config = settings.load_settings()
    my_company = config.get('company_details', {})
    
    try:
        with open('template.html', 'r') as file:
            html_content = file.read()
    except FileNotFoundError:
        print("!! Error: 'template.html' not found in the directory.")
        input("Press Enter to return...")
        return

    # 4. Build the Table Rows and Calculate Totals
    table_rows_html = ""
    total_po_value = 0.0
    
    for p_idx, m_idx, job_no, m_data in items_to_order:
        cost = m_data.get('estimated_cost', 0.0)
        total_po_value += cost
        table_rows_html += f"""
            <tr>
                <td>{job_no}</td>
                <td>{m_data.get('name', 'Unknown')}</td>
                <td>${cost:,.2f}</td>
            </tr>
        """
        logs[p_idx]['Materials'][m_idx]['procurement_status'] = 'Ordered'

    # 5. Inject Data into HTML
    date_str = datetime.now().strftime('%d-%m-%Y')
    po_number = f"PO-{datetime.now().strftime('%Y%m%d%H%M')}"
    
    # Inject PO Details
    html_content = html_content.replace('{{DATE}}', date_str)
    html_content = html_content.replace('{{PO_NUMBER}}', po_number)
    html_content = html_content.replace('{{QUOTE_REF}}', quote_ref if quote_ref else 'N/A')
    
    # Inject My Company Details (ATO Requirements)
    html_content = html_content.replace('{{MY_COMPANY_NAME}}', my_company.get('name', 'YOUR COMPANY NAME'))
    html_content = html_content.replace('{{MY_ABN}}', my_company.get('abn', 'YOUR ABN'))
    html_content = html_content.replace('{{MY_ADDRESS}}', my_company.get('address', 'YOUR ADDRESS'))
    html_content = html_content.replace('{{MY_PHONE}}', my_company.get('phone', 'YOUR PHONE'))
    html_content = html_content.replace('{{MY_EMAIL}}', my_company.get('email', 'YOUR EMAIL'))
    
    # Inject Supplier Details
    html_content = html_content.replace('{{SUPPLIER_NAME}}', selected_sup)
    html_content = html_content.replace('{{SUPPLIER_ABN}}', sup_details.get('abn', 'N/A'))
    html_content = html_content.replace('{{SUPPLIER_PHONE}}', sup_details.get('phone', 'N/A'))
    html_content = html_content.replace('{{SUPPLIER_ADDRESS}}', sup_details.get('address', 'N/A'))
    html_content = html_content.replace('{{PAYMENT_TERMS}}', sup_details.get('payment_details', 'N/A'))
    
    # Inject Table and Math
    html_content = html_content.replace('{{TABLE_ROWS}}', table_rows_html)
    html_content = html_content.replace('{{TOTAL_VALUE}}', f"{total_po_value:,.2f}")

    # 6. Generate the PDF
    filename = f"{po_number}_{selected_sup.replace(' ', '')}.pdf"
    with open(filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)

    if pisa_status.err:
        print("!! Error generating PDF.")
    else:
        storage.overwrite_db(logs)
        print(f"\n>> SUCCESS: PDF saved as '{filename}'")
        print(f">> Moved {len(items_to_order)} items to 'Ordered' status.")
    
    input("\nPress Enter to return...")