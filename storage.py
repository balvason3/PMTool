# --- BEDROCK: STORAGE MODULE (ORM ENABLED) ---
import json
from datetime import datetime
import settings
from database import Project, ProjectItem, Variation, get_session

def get_all_history():
    """Fetches all projects from the database and formats them for the CLI."""
    history = []
    
    # We use the session generator from database.py
    for db in get_session():
        # Query all projects
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
    """Generates the next sequential Quote Number (e.g., QT-1000)."""
    config = settings.load_settings()
    prefix = config.get('quote_prefix', 'QT-')
    start_number = config.get('quote_start', 1000)
    
    highest = start_number - 1
    
    for db in get_session():
        # Fetch only quote numbers that start with our prefix
        quotes = db.query(Project.Quote_Number).filter(
            Project.Quote_Number.like(f"{prefix}%")
        ).all()
        
        for (qid,) in quotes:
            if qid:
                try:
                    num = int(qid.replace(prefix, ""))
                    if num > highest:
                        highest = num
                except ValueError:
                    continue
                    
    return f"{prefix}{highest + 1}"

def generate_next_id():
    """Generates the next sequential Job Number (e.g., JN-10000)."""
    config = settings.load_settings()
    id_prefix = config.get('id_prefix', 'JN-')
    start_number = config.get('start_number', 10000)
    
    highest = start_number - 1
    
    for db in get_session():
        jobs = db.query(Project.Project_ID).filter(
            Project.Project_ID.like(f"{id_prefix}%")
        ).all()
        
        for (pid,) in jobs:
            if pid:
                try:
                    num = int(pid.replace(id_prefix, ""))
                    if num > highest:
                        highest = num
                except ValueError:
                    continue
            
    return f"{id_prefix}{highest + 1}"

def overwrite_db(history_list):
    """Legacy wrapper for batch updates (used by po_generator.py)."""
    for proj in history_list:
        update_project(None, proj)
        
def get_variations_by_project(internal_id):
    """Fetches all variations for a given project."""
    variations = []
    for db in get_session():
        vars = db.query(Variation).filter(
            Variation.project_id == internal_id
        ).all()
        for v in vars:
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
                "letter_sent_date": v.letter_sent_date
            })
    return variations

def save_variation(project_id, raised_by, scope, reason, cost_impact, programme_impact):
    """Creates a new variation in Draft status."""
    from datetime import datetime
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    for db in get_session():
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
        db.commit()
        return reference  # Return so the UI can confirm "V3 created"

def update_variation_status(variation_id, new_status, actioned_by):
    """Updates a variation status and records who actioned it and when."""
    from datetime import datetime
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    for db in get_session():
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

def save_to_db(name, scope, client, target_date, labor, materials, total_ex, gst, total_inc):
    """Creates a new estimate natively via SQLAlchemy."""
    quote_id = generate_next_quote_id()    
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    for db in get_session():
        new_project = Project(
            Quote_Number=quote_id,
            Status="Draft",
            Timestamp=now,
            Project_Name=name,
            Client=client,
            Target_Date=target_date,
            Scope=scope,
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

    for db in get_session():
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