Bedrock: Project & Procurement Manager
Bedrock is a lightweight, standalone command-line interface (CLI) application designed to help project managers and solo contractors track project estimates, manage budgets, and automate procurement.

Currently in active development, this tool bridges the gap between messy spreadsheets and expensive, bloated project management software.

🚀 Features
Project Estimating: Build quotes by calculating labor hours, material costs, markups, and GST.

Lifecycle Tracking: Track projects through various stages (Draft, Quoted, Active, Completed, Invoiced, Archived).

Live Dashboards: View real-time financial health, including base budgets, total markup, and non-billable variances.

Procurement Automation: Tag materials as "Ready to Order" across multiple active projects.

Supplier Database: Manage a built-in Supplier Database.

PDF Generation: Automatically generate professional, landscape-formatted PDF Purchase Orders ready to email to suppliers.

Global Settings: Customize your company details, default tax rates, and standard materials/roles.

💻 Installation Instructions (Standalone Executable)
You do not need to install Python or any external libraries to run Bedrock.

Step 1: Download the Application
Download the latest main.exe file from the Releases page. (Note: Be sure to update this link!)

Step 2: Setup your Workspace
Create a new folder on your computer (e.g., on your Desktop or in your Documents) and place the main.exe file inside it.
Note: When you run the application, it will automatically generate a data/ folder for your database and an exports/ folder for your PDF Purchase Orders in this same location.

Step 3: Run the Application
Double-click the main.exe file to start the program.

Troubleshooting Windows Defender: Because this is a custom, self-compiled application, Windows SmartScreen may flag it with a "Windows protected your PC" popup on the first launch. Click "More info" and then "Run anyway" to launch the tool.

🛠️ Getting Started (First Time Setup)
When you boot up Bedrock for the first time, follow these quick steps to get your environment ready:

Select Option 4: Global Settings from the Main Menu.

Select Option 7: Update Company Details.

Enter your business name, ABN, and contact details. This ensures your automatically generated Purchase Orders are compliant and professional.

Go back to the Main Menu and select Option 1: Create New Estimate to start your first project!

📢 Feedback & Bug Reports Requested!
This project is currently in early stages, and I am actively looking for feedback! If you download and use this tool, I want to hear from you. Please let me know:

Did you encounter any bugs, crashes, or weird behavior?

Is the workflow intuitive, or did you get stuck on a specific menu?

What features would make this actually usable for your daily workflow?

How to provide feedback:

Open an Issue on this GitHub repository.

Start a discussion in the GitHub Discussions tab.

Reach out to me directly at [Insert Your Email/Contact Info Here].

🗺️ Future Roadmap
Client Proposal Exporter: Generate client-facing PDF quotes that hide internal markup and labor rates.

Progress Claim Tracking: Log invoice stages (e.g., "50% Deposit Paid").

Database Upgrade: Transition from local .json storage to a robust SQLite database for faster querying and future multi-user support.
