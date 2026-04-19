# --- PMTool: METADATA MODULE ---

def get_project_metadata():
    """Collects client, timeline, scope, and method information."""
    print("\n--- PROJECT DETAILS ---")
    client = input("Client Name (or press Enter to leave as TBA): ").strip()
    target_date = input("Target Completion Date (e.g., DD/MM/YYYY) or press Enter to skip: ").strip()
    
    return {
        "client": client if client else "TBA",
        "target_date": target_date if target_date else "TBA"
    }

def get_scope_and_method():
    """Collects scope and method/approach for an estimate."""
    print("\n--- SCOPE & METHOD ---")
    scope = input("Scope of Work: ").strip()
    method = input("Method/Approach (How will the work be achieved?): ").strip()
    
    return {
        "scope": scope if scope else "TBA",
        "method": method if method else "TBA"
    }