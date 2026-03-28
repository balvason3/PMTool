# --- PMTool: TUTORIAL MODULE ---
import time

def run_demo():
    print("\n" + "="*60)
    print("   WELCOME TO BASELINE (PMTool) DEMO   ")
    print("="*60)
    
    screens = [
        "Baseline is designed to track your projects from initial Quote to Completion.\nHere is a quick overview of how it works:",
        "STEP 1: ESTIMATING\nYou create a new estimate by adding Labor Roles and Materials. Baseline calculates the Base Cost, applies your default Markup, and generates a total Sell Price.",
        "STEP 2: PROCUREMENT\nOnce an estimate becomes an 'Active' project, you can tag materials as 'Ready to Order', assign suppliers, and generate professional PDF Purchase Orders directly from the tool.",
        "STEP 3: TRACKING\nLog actual labor hours and material invoices against the active project to see your real-time profit margins and variances on the Project Dashboard."
    ]
    
    for i, screen in enumerate(screens):
        print(f"\n--- Screen {i+1} of {len(screens)} ---")
        print(screen)
        print("-" * 60)
        
        if i < len(screens) - 1:
            choice = input("Press Enter to continue, or type 'S' to skip demo: ").strip().upper()
            if choice == 'S':
                print("\n>> Exiting Demo.")
                break
    
    print("\n>> Demo Complete!")
    time.sleep(1)