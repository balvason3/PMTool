# --- PMTool: METADATA MODULE ---

def get_project_metadata():
    """Collects client and timeline information."""
    print("\n--- PROJECT DETAILS ---")
    client = input("Client Name (or press Enter to leave as TBA): ").strip()
    target_date = input("Target Completion Date (e.g., DD/MM/YYYY) or press Enter to skip: ").strip()
    
    return {
        "client": client if client else "TBA",
        "target_date": target_date if target_date else "TBA"
    }