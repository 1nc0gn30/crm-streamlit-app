📜 README.md

# 🗂️ Advanced CRM System (Streamlit Edition)

## 🚀 Overview
This is a **local-first, lightweight CRM system** built with **Streamlit**. It allows businesses to manage clients, tasks, notes, and analytics without needing a backend server. Data is stored locally in a JSON file.

## 🔥 Features
✅ **Client Management** (Add, Edit, Delete, Filter, Sort)  
✅ **Task Management** (Assign, Complete, Delete, Prioritize)  
✅ **Notes System** (Add & Manage Notes per Client)  
✅ **Lead Tracking** (Monitor Leads, Active & Inactive Clients)  
✅ **Follow-up Reminders** (Schedule follow-ups with clients)  
✅ **Export to CSV** (Download all client data in CSV format)  
✅ **Data Backup & Restore** (Export & Restore JSON Data)  
✅ **Analytics Dashboard** (Client Insights & Lead Source Breakdown)  
✅ **Interactive UI** (Tabs, Expander Panels, Charts)

## 📦 Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/1nc0gn30/crm-streamlit-app.git
   cd streamlit-crm
   ```
    Create a virtual environment (optional)
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate # On Windows
    ```
Install dependencies

```bash
pip install -r requirements.txt
```

Run the CRM app

    streamlit run crm_app.py

🎨 Screenshots

(Add screenshots of the CRM in action here!)
🔄 Data Storage

    All client data is stored in crm_data.json.
    No backend required; everything runs locally.

📤 Export & Backup

    Export client data to CSV.
    Backup/Restore JSON data.

🛠️ Tech Stack

    Frontend/UI: Streamlit
    Data Handling: JSON, Pandas
    Charts & Visualization: Plotly
    Form Handling: Streamlit Forms
    Unique Identifiers: UUID
    Date & Time: Datetime

🤝 Contributing

Contributions are welcome! Feel free to fork this repo and submit PRs. 🎉
⚖️ License

This project is open-source under the MIT License.

## **📜 requirements.txt**
```txt
streamlit
pandas
plotly# crm-streamlit-app
