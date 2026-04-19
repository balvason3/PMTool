# --- PMTool: ESTIMATING MODULE ---
import engine
import storage
import labour
import materials
import metadata

def create_estimate():
    print("\n--- CREATE NEW ESTIMATE ---")
    name = input("Project Name: ")
    scope = input("Scope: ")
    meta = metadata.get_project_metadata() 
    
    # 1. Get labor first
    labor = labour.get_labour_inputs()
    # 2. Pass labor INTO materials so assemblies can append to it!
    mats = materials.get_material_inputs(labor) 
    
    base = engine.calculate_totals(labor, mats)
    tax = engine.calculate_gst(base['total_ex'])
    
    # Save using the updated storage logic (Quote Number generation)
    storage.save_to_db(name, scope, meta['client'], meta['target_date'], labor, mats, base['total_ex'], tax['gst_value'], tax['total_inc_gst'])
    
    print("\n>> Saved as Draft.")