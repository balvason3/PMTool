# PMTool - Project Costing & Budgeting
import json

def calculate_budget():
    print("--- PMTool: Project Budget Estimator ---")
    
    # Input gathering
    project_name = input("Project Name: ")
    labor_hours = float(input("Estimated Labor Hours: "))
    hourly_rate = float(input("Hourly Rate ($): "))
    materials_cost = float(input("Total Materials Cost ($): "))
    
    # Logic
    subtotal = (labor_hours * hourly_rate) + materials_cost
    contingency = subtotal * 0.15  # Adding a 15% safety buffer
    total_estimate = subtotal + contingency

    # Output to screen
    print(f"\n--- Budget for {project_name} ---")
    print(f"Subtotal: ${subtotal:,.2f}")
    print(f"Contingency (15%): ${contingency:,.2f}")
    print(f"Total Estimate: ${total_estimate:,.2f}")

    # Save data for versioning
    budget_data = {
        "Project": project_name,
        "Total": total_estimate
    }
    
    with open('budgets.json', 'a') as f:
        json.dump(budget_data, f)
        f.write('\n')

if __name__ == "__main__":
    calculate_budget()