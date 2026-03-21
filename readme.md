BASEline: Project & Procurement Manager
BASEline is a lightweight, Python-based command-line interface (CLI) application designed to help project managers and solo contractors track project estimates, manage budgets, and automate procurement.

Currently in active development, this tool bridges the gap between messy spreadsheets and expensive, bloated project management software.

🚀 Features
Project Estimating: Build quotes by calculating labor hours, material costs, markups, and GST.

Lifecycle Tracking: Track projects through various stages (Draft, Quoted, Active, Completed, Invoiced, Archived).

Live Dashboards: View real-time financial health, including base budgets, total markup, and non-billable variances.

Procurement Automation: * Tag materials as "Ready to Order" across multiple active projects.

Manage a built-in Supplier Database.

Automatically generate professional, landscape-formatted PDF Purchase Orders ready to email to suppliers.

Global Settings: Customize your company details, default tax rates, and standard materials/roles.

💻 Installation Instructions
To run BASEline on your local machine, you will need to have Python 3 installed.

Step 1: Download the Project
Download or clone this repository to your local computer.

Bash
git clone https://github.com/YOUR-USERNAME/BASEline.git
Step 2: Install Dependencies
BASEline uses a lightweight external library (xhtml2pdf) to generate the PDF Purchase Orders. Open your terminal (or Command Prompt/PowerShell), navigate to the BASEline folder, and run:

Bash
pip install xhtml2pdf
(Note: If pip is not recognized on Windows, try running py -m pip install xhtml2pdf instead).

Step 3: Run the Application
Once the installation is complete, start the application by running:

Bash
python main.py
(On Windows, you can also use py main.py).

🛠️ Getting Started (First Time Setup)
When you boot up BASEline for the first time, follow these quick steps to get your environment ready:

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

Database Upgrade: Transition from local .json storage to a robust SQL database for faster querying and future multi-user support.
