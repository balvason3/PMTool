# --- BEDROCK: STORAGE MODULE (ORM ENABLED) ---
import json
from datetime import datetime
import settings
from sqlalchemy import func
from database import Project, ProjectItem, Variation, VariationItem, get_session, get_db_session

def get_all_history():
    """Fetches all projects from the database and formats them for the CLI."""
    history = []
    
    with get_db_session() as db:
        # Query all projects in one session
        projects = db.query(Project).all()
        
        for p in projects:
            # Reconstruct the dictionary format the CLI expects
            project_dict = {
                "internal_id": p.internal_id,
                "Project_ID": p.Project_ID,
                "Quote_Number": p.Quote_Number,
                "Status": p.Status,
                "Timestamp": p.Timestamp,
                "Project": p.Project_Name,
                "Client": p.Client,
                "Target_Date": p.Target_Date,
                "Scope": p.Scope,
                "Method": p.Method,
                "Version": p.Version,
                "Total_Ex_GST": p.Total_Ex_GST,
                "GST": p.GST,
                "Total_Inc_GST": p.Total_Inc_GST,
                "Labor": [],
                "Materials": [],
                "Notes": []
            }
            
            # Sort the associated items into their respective lists
            for item in p.items:
                parsed_data = json.loads(item.item_data)
                if item.item_type == 'Labor':
                    project_dict['Labor'].append(parsed_data)
                elif item.item_type == 'Material':
                    project_dict['Materials'].append(parsed_data)
                elif item.item_type == 'Note':
                    project_dict['Notes'].append(parsed_data)
                    
            history.append(project_dict)
            
    return history

def generate_next_quote_id():
    """Generates the next sequential Quote Number (e.g., QT-1000) using SQL MAX()."""
    config = settings.load_settings()
    prefix = config.get('quote_prefix', 'QT-')
    start_number = config.get('quote_start', 1000)
    
    with get_db_session() as db:
        # Use SQL MAX() to find the highest quote number efficiently
        result = db.query(func.max(Project.Quote_Number)).filter(
            Project.Quote_Number.like(f"{prefix}%")
        ).scalar()
        
        highest = start_number - 1
        if result:
            try:
                num = int(result.replace(prefix, ""))
                highest = num
            except (ValueError, AttributeError):
                pass
                    
    return f"{prefix}{highest + 1}"

def generate_next_id():
    """Generates the next sequential Job Number (e.g., JN-10000) using SQL MAX()."""
    config = settings.load_settings()
    id_prefix = config.get('id_prefix', 'JN-')
    start_number = config.get('start_number', 10000)
    
    with get_db_session() as db:
        # Use SQL MAX() to find the highest job ID efficiently
        result = db.query(func.max(Project.Project_ID)).filter(
            Project.Project_ID.like(f"{id_prefix}%")
        ).scalar()
        
        highest = start_number - 1
        if result:
            try:
                num = int(result.replace(id_prefix, ""))
                highest = num
            except (ValueError, AttributeError):
                pass
            
    return f"{id_prefix}{highest + 1}"

def overwrite_db(history_list):
    """Legacy wrapper for batch updates (used by po_generator.py)."""
    for proj in history_list:
        update_project(None, proj)
        
def get_variations_by_project(internal_id):
    """Fetches all variations for a given project including their items."""
    variations = []
    with get_db_session() as db:
        vars = db.query(Variation).filter(
            Variation.project_id == internal_id
        ).all()
        for v in vars:
            # Fetch variation items
            labor_items = []
            material_items = []
            for item in v.items:
                parsed_data = json.loads(item.item_data)
                if item.item_type == 'Labor':
                    labor_items.append(parsed_data)
                elif item.item_type == 'Material':
                    material_items.append(parsed_data)
            
            variations.append({
                "id": v.id,
                "project_id": v.project_id,
                "reference": v.reference,
                "status": v.status,
                "raised_by": v.raised_by,
                "raised_date": v.raised_date,
                "accepted_date": v.accepted_date,
                "accepted_by": v.accepted_by,
                "scope_description": v.scope_description,
                "reason": v.reason,
                "cost_impact": v.cost_impact,
                "programme_impact": v.programme_impact,
                "letter_sent": v.letter_sent,
                "letter_sent_date": v.letter_sent_date,
                "Labor": labor_items,
                "Materials": material_items
            })
    return variations

def save_variation(project_id, raised_by, scope, reason, cost_impact, programme_impact, labor=None, materials=None):
    """Creates a new variation in Draft status with optional labour and materials breakdown."""
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    if labor is None:
        labor = []
    if materials is None:
        materials = []
    
    with get_db_session() as db:
        # Auto-generate the reference number (V1, V2, V3...)
        existing_count = db.query(Variation).filter(
            Variation.project_id == project_id
        ).count()
        reference = f"V{existing_count + 1}"
        
        new_var = Variation(
            project_id=project_id,
            reference=reference,
            status="Draft",
            raised_by=raised_by,
            raised_date=now,
            scope_description=scope,
            reason=reason,
            cost_impact=cost_impact,
            programme_impact=programme_impact,
            letter_sent=False
        )
        db.add(new_var)
        db.flush()  # Generate the ID without committing
        
        # Attach labour and material items
        for l_item in labor:
            db.add(VariationItem(variation_id=new_var.id, item_type='Labor', item_data=json.dumps(l_item)))
        for m_item in materials:
            db.add(VariationItem(variation_id=new_var.id, item_type='Material', item_data=json.dumps(m_item)))
        
        db.commit()
        return reference

def update_variation_status(variation_id, new_status, actioned_by):
    """Updates a variation status and records who actioned it and when."""
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    with get_db_session() as db:
        var = db.query(Variation).filter(Variation.id == variation_id).first()
        if not var:
            return False, "Variation not found."
        
        var.status = new_status
        
        # If accepting, record who accepted and when
        if new_status == "Accepted":
            var.accepted_by = actioned_by
            var.accepted_date = now
            
        db.commit()
        return True, f"{var.reference} updated to {new_status}."

def save_to_db(name, scope, method, client, target_date, labor, materials, total_ex, gst, total_inc):
    """Creates a new estimate natively via SQLAlchemy."""
    quote_id = generate_next_quote_id()    
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    with get_db_session() as db:
        new_project = Project(
            Quote_Number=quote_id,
            Status="Draft",
            Timestamp=now,
            Project_Name=name,
            Client=client,
            Target_Date=target_date,
            Scope=scope,
            Method=method,
            Version="1.0",
            Total_Ex_GST=total_ex,
            GST=gst,
            Total_Inc_GST=total_inc
        )
        
        db.add(new_project)
        db.flush() # Flushes to generate the internal_id without committing yet
        
        # Attach the JSON items
        for l_item in labor:
            db.add(ProjectItem(project_id=new_project.internal_id, item_type='Labor', item_data=json.dumps(l_item)))
        for m_item in materials:
            db.add(ProjectItem(project_id=new_project.internal_id, item_type='Material', item_data=json.dumps(m_item)))
            
        db.commit()

def update_project(index, updated_data):
    """Updates an existing project and entirely replaces its items safely."""
    internal_id = updated_data.get('internal_id')
    
    if not internal_id:
        print("!! Critical Error: Cannot update project without internal_id.")
        return

    with get_db_session() as db:
        project = db.query(Project).filter(Project.internal_id == internal_id).first()
        
        if not project:
            return

        # Update core fields (convert empty strings to None for UNIQUE constraints)
        project.Project_ID = updated_data.get('Project_ID') or None
        project.Quote_Number = updated_data.get('Quote_Number') or None
        project.Status = updated_data.get('Status', 'Draft')
        project.Timestamp = updated_data.get('Timestamp', '')
        project.Project_Name = updated_data.get('Project', '')
        project.Client = updated_data.get('Client', '')
        project.Target_Date = updated_data.get('Target_Date', '')
        project.Scope = updated_data.get('Scope', '')
        project.Method = updated_data.get('Method', '')
        project.Version = updated_data.get('Version', '1.0')
        project.Total_Ex_GST = updated_data.get('Total_Ex_GST', 0.0)
        project.GST = updated_data.get('GST', 0.0)
        project.Total_Inc_GST = updated_data.get('Total_Inc_GST', 0.0)

        # Clear existing items
        db.query(ProjectItem).filter(ProjectItem.project_id == internal_id).delete()
        
        # Insert fresh items
        for l_item in updated_data.get('Labor', []):
            db.add(ProjectItem(project_id=internal_id, item_type='Labor', item_data=json.dumps(l_item)))
        for m_item in updated_data.get('Materials', []):
            db.add(ProjectItem(project_id=internal_id, item_type='Material', item_data=json.dumps(m_item)))
        for n_item in updated_data.get('Notes', []):
            db.add(ProjectItem(project_id=internal_id, item_type='Note', item_data=json.dumps(n_item)))
            
        db.commit()