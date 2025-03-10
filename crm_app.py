import streamlit as st
import json
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import csv
import io

# Define database file
DB_FILE = Path("crm_data.json")

# Load Data
def load_data():
    if DB_FILE.exists():
        try:
            with open(DB_FILE, "r") as file:
                data = json.load(file)
                if "clients" not in data:
                    data = {"clients": []}  # Fix missing key
        except json.JSONDecodeError:
            data = {"clients": []}  # Fix broken JSON
    else:
        data = {"clients": []}  # Initialize if file is missing

    return data  # Always return a valid dictionary

# Save Data
def save_data(data):
    if "clients" not in data:
        data = {"clients": []}  # Prevent saving a broken structure
    with open(DB_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Export to CSV
def export_to_csv(clients):
    output = io.StringIO()
    csv_writer = csv.writer(output)
    
    # Headers
    headers = ['ID', 'Name', 'Phone', 'Email', 'Status', 'Date Added', 'Value', 'Source']
    csv_writer.writerow(headers)
    
    # Data
    for client in clients:
        csv_writer.writerow([
            client.get('id', ''),
            client.get('name', ''),
            client.get('phone', ''),
            client.get('email', ''),
            client.get('status', ''),
            client.get('date_added', ''),
            client.get('value', 0),
            client.get('source', '')
        ])
    
    return output.getvalue()

# Initialize
st.set_page_config(page_title="CRM System", layout="wide")
st.title("🗂️ Advanced CRM System")

# Load Clients
data = load_data()
clients = data.get("clients", [])

# Ensure all clients have the new fields
for client in clients:
    if "date_added" not in client:
        client["date_added"] = datetime.now().strftime("%Y-%m-%d")
    if "value" not in client:
        client["value"] = 0
    if "source" not in client:
        client["source"] = "Direct"
    if "id" not in client or not client["id"]:
        client["id"] = str(uuid.uuid4())[:8]
    if "follow_up_date" not in client:
        client["follow_up_date"] = ""
    if "tags" not in client:
        client["tags"] = []

# Sidebar: Add New Client
with st.sidebar:
    st.header("Add New Client")
    with st.form("new_client_form"):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        status = st.selectbox("Status", ["Lead", "Active", "Inactive"])
        value = st.number_input("Potential Value ($)", min_value=0, step=100)
        source = st.selectbox("Lead Source", ["Direct", "Referral", "Website", "Social Media", "Event", "Other"])
        tags = st.multiselect("Tags", ["VIP", "New", "Priority", "Follow-up", "Onboarding", "Long-term"])
        follow_up_date = st.date_input("Follow-up Date", datetime.now() + timedelta(days=7))
        
        submit_button = st.form_submit_button("Add Client")
        
        if submit_button:
            if name and phone and email:
                new_client = {
                    "id": str(uuid.uuid4())[:8],
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "status": status,
                    "tasks": [],
                    "notes": [],
                    "date_added": datetime.now().strftime("%Y-%m-%d"),
                    "value": value,
                    "source": source,
                    "tags": tags,
                    "follow_up_date": follow_up_date.strftime("%Y-%m-%d")
                }
                clients.append(new_client)
                save_data({"clients": clients})
                st.success(f"Client {name} added!")
                st.rerun()

    # Quick Stats
    st.divider()
    st.subheader("Quick Stats")
    st.info(f"Total Clients: {len(clients)}")
    st.info(f"Tasks Due Today: {sum(1 for c in clients for t in c.get('tasks', []) if not t.get('completed', False))}")

# Tabs for Navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Clients", "✅ Tasks", "📝 Notes", "📊 Dashboard", "⚙️ Settings"])

### 📋 CLIENTS TAB ###
with tab1:
    st.subheader("Client Management")

    # Search & Filtering Section
    with st.expander("🔍 Search & Filter Options", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            search_query = st.text_input("Search Clients", "")
        with col2:
            filter_status = st.multiselect("Filter by Status", ["Lead", "Active", "Inactive"], default=[])
        
        col3, col4 = st.columns(2)
        with col3:
            sort_by = st.selectbox("Sort by", ["Date Added", "Name", "Status", "Value"])
        with col4:
            filter_tags = st.multiselect("Filter by Tags", ["VIP", "New", "Priority", "Follow-up", "Onboarding", "Long-term"], default=[])
    
    # Export Options
    export_col1, export_col2 = st.columns([3, 1])
    with export_col2:
        if st.button("📤 Export Clients (CSV)"):
            csv_data = export_to_csv(clients)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="crm_clients.csv",
                mime="text/csv"
            )
    
    # Sort clients
    if sort_by == "Name":
        clients = sorted(clients, key=lambda x: x["name"])
    elif sort_by == "Status":
        clients = sorted(clients, key=lambda x: x["status"])
    elif sort_by == "Value":
        clients = sorted(clients, key=lambda x: x.get("value", 0), reverse=True)
    else:  # Date Added
        clients = sorted(clients, key=lambda x: x.get("date_added", ""), reverse=True)

    # Filter by search query and other filters
    filtered_clients = clients
    
    if search_query:
        filtered_clients = [c for c in filtered_clients if search_query.lower() in c["name"].lower() or 
                           search_query.lower() in c.get("email", "").lower() or 
                           search_query.lower() in c.get("phone", "").lower()]
    
    if filter_status:
        filtered_clients = [c for c in filtered_clients if c["status"] in filter_status]
        
    if filter_tags:
        filtered_clients = [c for c in filtered_clients if any(tag in c.get("tags", []) for tag in filter_tags)]

    # Display client table with enhanced columns
    if filtered_clients:
        client_data = []
        for c in filtered_clients:
            client_data.append({
                'ID': c["id"],
                'Name': c["name"],
                'Email': c["email"],
                'Phone': c["phone"],
                'Status': c["status"],
                'Date Added': c.get("date_added", ""),
                'Value ($)': c.get("value", 0),
                'Source': c.get("source", ""),
                'Follow-up': c.get("follow_up_date", ""),
                'Tasks': len([t for t in c.get("tasks", []) if not t.get("completed", False)]),
                'Tags': ", ".join(c.get("tags", []))
            })
        
        df = pd.DataFrame(client_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No clients found!")

    # Client Detail View
    st.divider()
    st.subheader("Client Details & Edit")
    
    if clients:
        selected_id = st.selectbox("Select Client", [f"{c['name']} ({c['id']})" for c in clients])
        selected_id = selected_id.split("(")[1].split(")")[0]  # Extract ID from formatted string
        selected_client = next((c for c in clients if c["id"] == selected_id), None)

        if selected_client:
            # Client Profile
            profile_col1, profile_col2 = st.columns([2, 1])
            
            with profile_col1:
                st.subheader(f"{selected_client['name']}")
                st.markdown(f"📧 Email: **{selected_client['email']}**")
                st.markdown(f"📱 Phone: **{selected_client['phone']}**")
                st.markdown(f"📊 Status: **{selected_client['status']}**")
                st.markdown(f"💰 Potential Value: **${selected_client.get('value', 0):,}**")
                st.markdown(f"📅 Follow-up Date: **{selected_client.get('follow_up_date', '')}**")
                st.markdown(f"🔖 Tags: **{', '.join(selected_client.get('tags', []))}**")
            
            with profile_col2:
                st.markdown("**Quick Actions**")
                if st.button("📧 Send Email"):
                    st.info(f"Opening email to: {selected_client['email']}")
                if st.button("📱 Call Client"):
                    st.info(f"Dialing: {selected_client['phone']}")
                if st.button("📅 Schedule Follow-up"):
                    st.date_input("Select date", key="follow_up_widget")

            # Edit Client Form
            with st.expander("✏️ Edit Client", expanded=False):
                with st.form("edit_client_form"):
                    new_name = st.text_input("Name", selected_client["name"])
                    new_phone = st.text_input("Phone", selected_client["phone"])
                    new_email = st.text_input("Email", selected_client["email"])
                    new_status = st.selectbox("Status", ["Lead", "Active", "Inactive"], index=["Lead", "Active", "Inactive"].index(selected_client["status"]))
                    new_value = st.number_input("Potential Value ($)", min_value=0, value=selected_client.get("value", 0), step=100)
                    new_source = st.selectbox("Lead Source", ["Direct", "Referral", "Website", "Social Media", "Event", "Other"], index=["Direct", "Referral", "Website", "Social Media", "Event", "Other"].index(selected_client.get("source", "Direct")))
                    new_tags = st.multiselect("Tags", ["VIP", "New", "Priority", "Follow-up", "Onboarding", "Long-term"], default=selected_client.get("tags", []))
                    new_follow_up = st.date_input("Follow-up Date", datetime.strptime(selected_client.get("follow_up_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d") if selected_client.get("follow_up_date") else datetime.now())
                    
                    update_button = st.form_submit_button("Update Client")
                    
                    if update_button:
                        selected_client["name"] = new_name
                        selected_client["phone"] = new_phone
                        selected_client["email"] = new_email
                        selected_client["status"] = new_status
                        selected_client["value"] = new_value
                        selected_client["source"] = new_source
                        selected_client["tags"] = new_tags
                        selected_client["follow_up_date"] = new_follow_up.strftime("%Y-%m-%d")
                        save_data({"clients": clients})
                        st.success("Client updated successfully!")
                        st.rerun()
            
            # Delete Client
            with st.expander("🗑️ Delete Client", expanded=False):
                st.warning(f"Are you sure you want to delete {selected_client['name']}?")
                confirm_delete = st.text_input("Type client name to confirm deletion")
                if st.button("Delete Permanently") and confirm_delete == selected_client['name']:
                    clients = [c for c in clients if c["id"] != selected_id]
                    save_data({"clients": clients})
                    st.error(f"Client {selected_client['name']} deleted.")
                    st.rerun()

### ✅ TASKS TAB ###
with tab2:
    st.subheader("Task Management")
    
    # Task Dashboard
    col1, col2, col3 = st.columns(3)
    all_tasks = [{"client_id": c["id"], "client_name": c["name"], "task": t["task"], "completed": t.get("completed", False), "due_date": t.get("due_date", ""), "priority": t.get("priority", "Medium")} 
                for c in clients for t in c.get("tasks", [])]
    
    with col1:
        st.metric("Total Tasks", len(all_tasks))
    with col2:
        st.metric("Completed", len([t for t in all_tasks if t["completed"]]))
    with col3:
        st.metric("Pending", len([t for t in all_tasks if not t["completed"]]))
    
    # Task Filters
    task_col1, task_col2 = st.columns(2)
    with task_col1:
        task_filter = st.selectbox("View", ["All Tasks", "Pending Tasks", "Completed Tasks", "Due Today"])
    with task_col2:
        task_sort = st.selectbox("Sort By", ["Priority", "Due Date", "Client Name"])
    
    # Task List
    st.subheader("Task List")
    
    filtered_tasks = all_tasks
    if task_filter == "Pending Tasks":
        filtered_tasks = [t for t in all_tasks if not t["completed"]]
    elif task_filter == "Completed Tasks":
        filtered_tasks = [t for t in all_tasks if t["completed"]]
    elif task_filter == "Due Today":
        today = datetime.now().strftime("%Y-%m-%d")
        filtered_tasks = [t for t in all_tasks if t.get("due_date") == today and not t["completed"]]
    
    # Sort tasks
    if task_sort == "Priority":
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        filtered_tasks = sorted(filtered_tasks, key=lambda x: priority_order.get(x.get("priority", "Medium"), 1))
    elif task_sort == "Due Date":
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x.get("due_date", "9999-99-99"))
    else:  # Client Name
        filtered_tasks = sorted(filtered_tasks, key=lambda x: x["client_name"])
    
    if filtered_tasks:
        for idx, task in enumerate(filtered_tasks):
            task_col1, task_col2, task_col3 = st.columns([5, 2, 1])
            task_status = "✅" if task["completed"] else "⏳"
            priority_color = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}.get(task.get("priority", "Medium"), "🟠")
            
            with task_col1:
                st.markdown(f"{priority_color} **{task['client_name']}**: {task['task']} {task_status}")
                if task.get("due_date"):
                    st.caption(f"Due: {task.get('due_date', '')}")
            
            with task_col2:
                # Find the client and task index
                client = next((c for c in clients if c["id"] == task["client_id"]), None)
                if client:
                    task_idx = next((i for i, t in enumerate(client.get("tasks", [])) if t["task"] == task["task"]), None)
                    
                    if task_idx is not None:
                        if task["completed"]:
                            if st.button(f"Mark Incomplete", key=f"incomplete_{idx}"):
                                client["tasks"][task_idx]["completed"] = False
                                save_data({"clients": clients})
                                st.rerun()
                        else:
                            if st.button(f"Mark Complete", key=f"complete_{idx}"):
                                client["tasks"][task_idx]["completed"] = True
                                save_data({"clients": clients})
                                st.rerun()
            
            with task_col3:
                if st.button(f"🗑️", key=f"delete_task_{idx}"):
                    client = next((c for c in clients if c["id"] == task["client_id"]), None)
                    if client:
                        task_idx = next((i for i, t in enumerate(client.get("tasks", [])) if t["task"] == task["task"]), None)
                        if task_idx is not None:
                            client["tasks"].pop(task_idx)
                            save_data({"clients": clients})
                            st.rerun()
    else:
        st.info("No tasks found matching your criteria.")
    
    # Add Task to Client
    st.divider()
    st.subheader("Add New Task")
    
    if clients:
        with st.form("add_task_form"):
            task_client_id = st.selectbox("Select Client", [f"{c['name']} ({c['id']})" for c in clients], key="new_task_client")
            selected_client_id = task_client_id.split("(")[1].split(")")[0]
            task_desc = st.text_input("Task Description")
            task_priority = st.select_slider("Priority", options=["Low", "Medium", "High"], value="Medium")
            task_due_date = st.date_input("Due Date", datetime.now() + timedelta(days=3))
            
            task_submit = st.form_submit_button("Add Task")
            
            if task_submit and task_desc:
                selected_client = next((c for c in clients if c["id"] == selected_client_id), None)
                if selected_client:
                    new_task = {
                        "task": task_desc,
                        "completed": False,
                        "priority": task_priority,
                        "due_date": task_due_date.strftime("%Y-%m-%d"),
                        "created_at": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    if "tasks" not in selected_client:
                        selected_client["tasks"] = []
                        
                    selected_client["tasks"].append(new_task)
                    save_data({"clients": clients})
                    st.success("Task added successfully!")
                    st.rerun()

### 📝 NOTES TAB ###
with tab3:
    st.subheader("Client Notes")
    
    if clients:
        notes_client = st.selectbox("Select Client", [f"{c['name']} ({c['id']})" for c in clients], key="notes_client_select")
        selected_client_id = notes_client.split("(")[1].split(")")[0]
        selected_client = next((c for c in clients if c["id"] == selected_client_id), None)
        
        if selected_client:
            st.write(f"Notes for **{selected_client['name']}**")
            
            # Add new note
            with st.form("add_note_form"):
                note_text = st.text_area("New Note", height=100)
                note_submit = st.form_submit_button("Add Note")
                
                if note_submit and note_text:
                    if "notes" not in selected_client:
                        selected_client["notes"] = []
                        
                    new_note = {
                        "text": note_text,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "id": str(uuid.uuid4())[:8]
                    }
                    
                    selected_client["notes"].insert(0, new_note)  # Add to beginning
                    save_data({"clients": clients})
                    st.success("Note added!")
                    st.rerun()
            
            # Display existing notes
            if "notes" in selected_client and selected_client["notes"]:
                for idx, note in enumerate(selected_client["notes"]):
                    with st.expander(f"Note from {note.get('date', 'Unknown date')}", expanded=idx==0):
                        st.write(note.get("text", ""))
                        
                        note_col1, note_col2 = st.columns([5, 1])
                        with note_col2:
                            if st.button("Delete", key=f"delete_note_{idx}"):
                                selected_client["notes"].pop(idx)
                                save_data({"clients": clients})
                                st.rerun()
            else:
                st.info("No notes yet for this client.")
    else:
        st.warning("No clients found. Add a client first.")

### 📊 DASHBOARD TAB ###
with tab4:
    st.subheader("📊 CRM Analytics Dashboard")

    # Key Metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    num_clients = len(clients)
    num_leads = sum(1 for c in clients if c["status"] == "Lead")
    num_active = sum(1 for c in clients if c["status"] == "Active")
    num_inactive = sum(1 for c in clients if c["status"] == "Inactive")
    total_value = sum(c.get("value", 0) for c in clients)
    
    with metric_col1:
        st.metric("Total Clients", num_clients)
    with metric_col2:
        st.metric("Leads", num_leads)
    with metric_col3:
        st.metric("Active Clients", num_active)
    with metric_col4:
        st.metric("Total Value", f"${total_value:,}")
    
    # Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Client Status Breakdown")
        status_counts = {"Lead": num_leads, "Active": num_active, "Inactive": num_inactive}
        fig1 = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            color=list(status_counts.keys()),
            color_discrete_map={'Lead': '#FFC107', 'Active': '#4CAF50', 'Inactive': '#F44336'},
            hole=0.4
        )
        fig1.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig1, use_container_width=True)
    
    with chart_col2:
        st.subheader("Lead Sources")
    
    # Count sources
        source_data = {}
        for client in clients:
            source = client.get("source", "Direct")
            source_data[source] = source_data.get(source, 0) + 1
    
    # Convert to DataFrame
        if source_data:
            source_df = pd.DataFrame({
                "Source": list(source_data.keys()),
                "Count": list(source_data.values())
            })

            fig2 = px.bar(
                source_df,
                x="Source",
                y="Count",
                labels={'x': 'Source', 'y': 'Number of Clients'},
                color="Source"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No lead source data available yet.")

    
    # Client Value Analysis
    st.subheader("Client Value Analysis")
    
    # Create data for the chart
    value_data = []
    for client in clients:
        if client.get("value", 0) > 0:
            value_data.append({
                "name": client["name"],
                "value": client.get("value", 0),
                "status": client["status"]
            })
    
    if value_data:
        value_df = pd.DataFrame(value_data).sort_values("value", ascending=False).head(10)
        fig3 = px.bar(
            value_df,
            x="name",
            y="value",
            color="status",
            title="Top 10 Clients by Value",
            labels={"name": "Client", "value": "Value ($)", "status": "Status"},
            color_discrete_map={'Lead': '#FFC107', 'Active': '#4CAF50', 'Inactive': '#F44336'}
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No client value data available yet.")
    
    # Recent Activities
    st.subheader("Recent Activities")
    
    # Collect recent activities (notes and tasks)
    activities = []
    
    for client in clients:
        for note in client.get("notes", []):
            activities.append({
                "client": client["name"],
                "type": "Note",
                "date": note.get("date", ""),
                "content": note.get("text", "")[:50] + "..." if len(note.get("text", "")) > 50 else note.get("text", "")
            })
        
        for task in client.get("tasks", []):
            activities.append({
                "client": client["name"],
                "type": "Task",
                "date": task.get("created_at", ""),
                "content": task.get("task", ""),
                "completed": task.get("completed", False)
            })
    
    # Sort by date (recent first) and take the top 10
    activities = sorted(activities, key=lambda x: x.get("date", ""), reverse=True)[:10]
    
    if activities:
        activity_df = pd.DataFrame(activities)
        st.dataframe(activity_df, use_container_width=True)
    else:
        st.info("No recent activities yet.")

### ⚙️ SETTINGS TAB ###
with tab5:
    st.subheader("⚙️ System Settings")
    
    settings_col1, settings_col2 = st.columns(2)
    
    with settings_col1:
        st.subheader("Data Management")
        
        if st.button("Backup Data"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_data = json.dumps(data, indent=4)
            st.download_button(
                label="Download Backup",
                data=backup_data,
                file_name=f"crm_backup_{timestamp}.json",
                mime="application/json"
            )
            st.success("Backup file created!")
        
        st.divider()
        
        with st.expander("Restore Data"):
            uploaded_file = st.file_uploader("Upload backup file", type=["json"])
            if uploaded_file is not None:
                try:
                    restore_data = json.loads(uploaded_file.getvalue().decode())
                    if st.button("Restore from Backup"):
                        save_data(restore_data)
                        st.success("Data restored successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error restoring data: {e}")
    
    with settings_col2:
        st.subheader("Customization")
        
        lead_status_options = st.text_input("Client Status Options (comma-separated)", "Lead, Active, Inactive")
        lead_source_options = st.text_input("Lead Source Options (comma-separated)", "Direct, Referral, Website, Social Media, Event, Other")
        tag_options = st.text_input("Tag Options (comma-separated)", "VIP, New, Priority, Follow-up, Onboarding, Long-term")
        
        if st.button("Save Settings"):
            # In a real app, we would save these to a settings file
            st.success("Settings saved!")
        
        st.divider()
        
        st.subheader("Advanced")
        
        dangerous_col1, dangerous_col2 = st.columns(2)
        with dangerous_col1:
            if st.button("Clear All Tasks"):
                if st.session_state.get("confirm_clear_tasks", False):
                    for client in clients:
                        client["tasks"] = []
                    save_data({"clients": clients})
                    st.session_state.confirm_clear_tasks = False
                    st.success("All tasks cleared!")
                    st.rerun()
                else:
                    st.session_state.confirm_clear_tasks = True
                    st.warning("Click again to confirm clearing all tasks")
        
        with dangerous_col2:
            if st.button("Reset CRM"):
                if st.session_state.get("confirm_reset", False):
                    save_data({"clients": []})
                    st.session_state.confirm_reset = False
                    st.success("CRM reset complete!")
                    st.rerun()
                else:
                    st.session_state.confirm_reset = True
                    st.warning("⚠️ This will delete ALL data. Click again to confirm.")