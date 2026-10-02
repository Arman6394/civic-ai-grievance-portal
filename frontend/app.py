import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import base64
from datetime import datetime, timedelta

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Grievance & Intelligent Routing Portal",
    page_icon="🏛️",
    layout="wide"
)

# ----------------------------------------------------
# STYLING & ANIMATIONS
# ----------------------------------------------------
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #3b82f6;
    }
    div[data-testid="stExpander"] {
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    div.stButton > button[kind="primary"] {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.6);
        transform: scale(1.01);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏛️ AI-Powered Public Grievance & Intelligent Routing Portal")

SLA_HOURS = {
    "P1": 6,
    "P2": 24,
    "P3": 72,
    "P4": 168
}

WARD_COORDINATES = {
    "Ward 10 - Central": {"lat": 26.8467, "lon": 80.9462},
    "Ward 12 - North Crossing": {"lat": 26.8920, "lon": 80.9580},
    "Ward 15 - Industrial Sector": {"lat": 26.8150, "lon": 80.8920},
    "Ward 22 - Green Park": {"lat": 26.8620, "lon": 80.9950}
}

WARD_COLOR_PALETTE = {
    "Ward 10 - Central": "#0d47a1",          # Deep Navy Blue
    "Ward 12 - North Crossing": "#b71c1c",     # Dark Crimson Red
    "Ward 15 - Industrial Sector": "#1b5e20",  # Dark Forest Green
    "Ward 22 - Green Park": "#4a148c"         # Deep Indigo
}

DEPARTMENT_SOPS = {
    "Electricity": {
        "P1": {
            "action": "Immediate Grid Isolation & Emergency Line Crew Dispatch",
            "crew": "1x Junior Engineer + 3x High-Tension Linemen",
            "equipment": "Insulated Bucket Truck, Arc Flash Suits, Fault Locator",
            "safety_note": "Cut substation breaker feed prior to site inspection."
        },
        "P2": {
            "action": "Distribution Transformer & Feeder Cable Inspection",
            "crew": "2x Certified Linemen",
            "equipment": "Step-ladder, Multimeter, Replacement Fuses",
            "safety_note": "Deploy road safety cones around roadside transformer boxes."
        },
        "default": {
            "action": "Routine Streetlight & Line Maintenance Inspection",
            "crew": "1x Field Electrician",
            "equipment": "Standard Lineman Toolset",
            "safety_note": "Conduct survey during scheduled daytime maintenance."
        }
    },
    "Water Supply": {
        "P1": {
            "action": "Main Line Valve Shutdown & High-Capacity Suction De-watering",
            "crew": "1x Hydraulic Engineer + 4x Pipeline Technicians",
            "equipment": "Excavator/JCB, High-Pressure Pipe Sealers, Submersible Pumps",
            "safety_note": "Issue emergency boil-water / low-pressure advisory to ward residents."
        },
        "P2": {
            "action": "Distribution Conduit Leak Patching & Sluice Valve Repair",
            "crew": "2x Plumbers + 2x Labor Assistants",
            "equipment": "Pipe Clamp Set, Trenching Spades, Pressure Gauges",
            "safety_note": "Coordinate traffic redirection if leakage is on a main road."
        },
        "default": {
            "action": "Meter Inspection, Contamination Testing & Valve Servicing",
            "crew": "1x Water Quality Inspector",
            "equipment": "Water Sampling Kit, Valve Keys",
            "safety_note": "Log contamination lab samples within 4 hours."
        }
    },
    "Sanitation / Waste Management": {
        "P1": {
            "action": "Hazardous Bio-waste / Chemical Spillage Emergency Clearance",
            "crew": "1x Sanitary Inspector + 4x Hazmat-Trained Workers",
            "equipment": "Bio-hazard Disposal Bags, PPE Coveralls, Bleaching/Disinfectant Sprayers",
            "safety_note": "Cordon off an 8-meter containment radius from pedestrian traffic."
        },
        "P2": {
            "action": "Community Dump Overflow Clearing & Secondary Transfer Transport",
            "crew": "1x Driver + 3x Sanitation Workers",
            "equipment": "Mini Tipper Truck, Mechanical Sweeper, Disinfectant",
            "safety_note": "Spray lime powder post-evacuation to deter vermin."
        },
        "default": {
            "action": "Scheduled Door-to-Door Route Audit & Secondary Bin Emptying",
            "crew": "Standard Route Crew",
            "equipment": "Compactor Truck, Wheelbarrows",
            "safety_note": "Ensure segregated green/blue bin compliance."
        }
    },
    "Roads & Infrastructure": {
        "P1": {
            "action": "Structural Cave-in / Sinkhole Emergency Barrier & Diversion Setup",
            "crew": "1x Executive Engineer + 4x Road Crew",
            "equipment": "Barricades, High-Visibility Hazard Flashers, Cold Asphalt Patch Mix",
            "safety_note": "Coordinate immediately with Traffic Police nodal officers."
        },
        "P2": {
            "action": "Deep Pothole Asphalt Compaction & Kerb Re-alignment",
            "crew": "1x Mason + 3x Asphalt Operators",
            "equipment": "Roller Compactor, Bitumen Emulsion Sprayer, Jackhammer",
            "safety_note": "Place reflective warning boards 50 meters ahead of work site."
        },
        "default": {
            "action": "Footpath Pavement Tile Repair & Drainage Grate Inspection",
            "crew": "2x Civil Maintenance Workers",
            "equipment": "Concrete Mortar, Hand Trowels, Grate Hooks",
            "safety_note": "Inspect during off-peak morning hours."
        }
    }
}

def get_action_recommendation(department, priority):
    dept_rules = DEPARTMENT_SOPS.get(department, {})
    return dept_rules.get(priority, dept_rules.get("default", {
        "action": "Assign standard field assessment team to verify incident veracity.",
        "crew": "1x Ward Surveyor",
        "equipment": "Inspection Tablet / Digital Audit Form",
        "safety_note": "Follow standard municipal field assessment protocols."
    }))

def calculate_sla(created_at_str, priority_level, status):
    if status in ["Resolved", "Officially Closed"]:
        return "✅ Resolved on Time", False
    try:
        clean_time_str = created_at_str.replace("Z", "").split(".")[0]
        created_time = datetime.fromisoformat(clean_time_str)
        allowed_hours = SLA_HOURS.get(priority_level, 72)
        deadline = created_time + timedelta(hours=allowed_hours)
        now = datetime.utcnow()
        remaining = deadline - now
        if remaining.total_seconds() <= 0:
            overdue = abs(remaining)
            hours_over = int(overdue.total_seconds() // 3600)
            return f"🚨 SLA BREACHED (+{hours_over}h overdue)", True
        else:
            hours_left = int(remaining.total_seconds() // 3600)
            mins_left = int((remaining.total_seconds() % 3600) // 60)
            return f"⏱️ {hours_left}h {mins_left}m remaining", False
    except Exception:
        return "SLA Active", False

def extract_image_and_text(raw_text):
    if not raw_text:
        return "", None
    if "[ATTACHED_IMAGE_BASE64:" in raw_text:
        parts = raw_text.split("[ATTACHED_IMAGE_BASE64:")
        clean_text = parts[0].strip()
        img_b64 = parts[1].rstrip("]").strip()
        return clean_text, img_b64
    return raw_text, None

def render_sms_dispatch_card(phone_number, tracking_id, dept, status, custom_msg=None):
    timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    if not custom_msg:
        msg_body = f"MUNICIPAL CITIZEN ALERT: Your ticket [{tracking_id}] under {dept} is now marked as '{status}'. Track live updates via portal."
    else:
        msg_body = custom_msg

    st.markdown(
        f"""
        <div style="background: rgba(16, 185, 129, 0.05); border: 1px dashed #10b981; border-radius: 8px; padding: 12px; margin-top: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: 600; color: #34d399; font-size: 0.9rem;">📲 Outbound Telecom Gateway Dispatched (Simulated API)</span>
                <span style="font-size: 0.75rem; color: #94a3b8;">{timestamp}</span>
            </div>
            <div style="font-size: 0.85rem; color: #cbd5e1; font-family: monospace;">
                <b>Recipient:</b> +91-{phone_number}<br>
                <b>Route:</b> NIC-GOV-SMS-PROMOTIONAL-ROUTE-1<br>
                <b>Payload:</b> "{msg_body}"
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

menu = st.sidebar.radio(
    "Navigation", 
    ["Citizen: File a Grievance", "Citizen: Track Ticket Status", "Officer / Admin Dashboard"]
)

# ----------------------------------------------------
# 1. CITIZEN: FILE GRIEVANCE
# ----------------------------------------------------
if menu == "Citizen: File a Grievance":
    st.header("📝 Submit a New Grievance")
    st.caption("Enter your grievance in natural plain language. The AI system will detect the department, severity, and potential duplicates.")

    col1, col2 = col1_val, col2_val = st.columns(2)
    with col1:
        citizen_name = st.text_input("Your Full Name", value="Rahul Sharma")
        location = st.selectbox("Select Ward / Locality", ["Ward 10 - Central", "Ward 12 - North Crossing", "Ward 15 - Industrial Sector", "Ward 22 - Green Park"])
    with col2:
        citizen_phone = st.text_input("Contact Number", value="9876543210")

    st.markdown("##### 🎙️ Voice Dictation or Text Input")
    col_dict1, col_dict2 = st.columns([3, 1])
    with col_dict1:
        st.caption("Type manually below, or upload an audio voice note of the grievance.")
    with col_dict2:
        use_voice = st.checkbox("🎙️ Use Audio Upload", help="Upload a WAV/MP3 voice recording")

    if use_voice:
        audio_file = st.file_uploader("Upload Voice Note (WAV / MP3)", type=["wav", "mp3"])
        if audio_file is not None:
            st.audio(audio_file)
            st.info("💡 Audio recorded. Enter or verify the transcribing key notes in the box below.")

    complaint_text = st.text_area(
        "Describe your grievance / issue in detail:", 
        height=130,
        placeholder="e.g. Major clean drinking water pipe burst on the main junction, road completely flooded..."
    )

    uploaded_image = st.file_uploader(
        "📸 Attach Photo Evidence (Optional - JPG/PNG):", 
        type=["jpg", "jpeg", "png"],
        help="Upload an image showing the hazard, leak, pothole, or garbage pile."
    )

    image_base64 = None
    if uploaded_image is not None:
        image_bytes = uploaded_image.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        st.image(image_bytes, caption="Uploaded Evidence Preview", width=220)

    if st.button("Submit Grievance to AI Router", type="primary", use_container_width=True):
        if not complaint_text.strip():
            st.error("Please enter a description of the issue.")
        else:
            final_description = complaint_text.strip()
            if image_base64:
                final_description += f"\n\n[ATTACHED_IMAGE_BASE64:{image_base64}]"

            payload = {
                "citizen_name": citizen_name,
                "citizen_phone": citizen_phone,
                "description": final_description,
                "location": location
            }
            try:
                res = requests.post(f"{API_URL}/api/complaints", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    st.toast("Grievance registered and routed successfully!", icon="🚀")
                    st.success("✅ Grievance Registered and Processed!")
                    st.metric("Your Tracking ID", data["tracking_id"])
                    
                    ai_meta = data["ai_analysis"]
                    dup_meta = data.get("duplicate_detection", {})
                    
                    is_dup = dup_meta.get("is_duplicate", False)
                    sim_val = dup_meta.get("similarity", 0.0)
                    parent_ref = dup_meta.get("parent_id")

                    confirm_sms = (
                        f"Namaste {citizen_name}, your grievance [{data['tracking_id']}] "
                        f"for {ai_meta['predicted_department']} has been registered under "
                        f"priority {ai_meta['priority_level']}. Resolution SLA target: "
                        f"{SLA_HOURS.get(ai_meta['priority_level'], 72)}h."
                    )
                    render_sms_dispatch_card(
                        citizen_phone, 
                        data["tracking_id"], 
                        ai_meta["predicted_department"], 
                        "Pending", 
                        confirm_sms
                    )

                    if is_dup or sim_val >= 0.45:
                        match_pct = int(sim_val * 100)
                        st.warning(
                            f"⚠️ **SEMANTIC DUPLICATE INCIDENT DETECTED ({match_pct}% Match)!**\n\n"
                            f"An existing open complaint (`{parent_ref}`) is already active in **{location}**.\n\n"
                            f"Your report has been merged into this primary ticket to avoid redundant resource allocation."
                        )
                    else:
                        st.info(f"✨ Fresh Incident Logged (Highest Locality Similarity: {int(sim_val * 100)}%)")
                    
                    st.subheader("🤖 AI Classification Insights")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Predicted Department", ai_meta["predicted_department"])
                    c2.metric("Confidence Score", f"{int(ai_meta['confidence_score'] * 100)}%")
                    c3.metric("Urgency Priority", ai_meta["priority_level"])
                    
                    if ai_meta["needs_human_triage"]:
                        st.warning("⚠️ Low AI confidence: Flagged for Human Nodal Review.")
                    else:
                        st.info(f"⚡ Auto-assigned directly to **{ai_meta['predicted_department']}** nodal officer queue.")
                else:
                    st.error("Failed to submit grievance.")
            except Exception as e:
                st.error(f"Could not connect to backend server: {e}")

# ----------------------------------------------------
# 2. CITIZEN: TRACK STATUS & CLOSED-LOOP AUDIT
# ----------------------------------------------------
# ----------------------------------------------------
# 2. CITIZEN: TRACK STATUS & CLOSED-LOOP AUDIT
# ----------------------------------------------------
elif menu == "Citizen: Track Ticket Status":
    st.header("🔍 Track Grievance Status")
    
    # State storage to prevent resetting on button clicks
    if "active_track_id" not in st.session_state:
        st.session_state["active_track_id"] = ""

    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        track_input = st.text_input(
            "Enter your Tracking ID (e.g. GRV-A1B2C3)", 
            value=st.session_state["active_track_id"]
        ).strip().upper()
    with search_col2:
        st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Check Status", type="primary", use_container_width=True):
            st.session_state["active_track_id"] = track_input

    # Keep rendering the ticket as long as an active ID is selected
    current_search_id = st.session_state["active_track_id"]
    if current_search_id:
        try:
            res = requests.get(f"{API_URL}/api/complaints/track/{current_search_id}")
            if res.status_code == 200:
                t = res.json()
                st.success(f"Record Found: {current_search_id}")
                
                status_val = t["status"]
                step_map = {
                    "Pending": 25, 
                    "In Progress": 50, 
                    "Resolved": 75, 
                    "Pending Citizen Verification": 85,
                    "Officially Closed": 100, 
                    "Duplicate Linked": 100,
                    "Reopened & Escalated (P1)": 30
                }
                prog_val = step_map.get(status_val, 25)
                
                st.write(f"**Resolution Lifecycle:** `{status_val}`")
                st.progress(prog_val)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Status", t["status"])
                col2.metric("Routed Department", t["predicted_department"])
                col3.metric("Urgency Priority", t["priority_level"])
                
                if t.get("is_duplicate"):
                    st.info(f"🔗 Linked as duplicate of primary incident: **{t.get('parent_ticket_id')}**")
                
                sla_info, _ = calculate_sla(t['created_at'], t['priority_level'], t['status'])
                st.markdown(f"**Resolution SLA:** `{sla_info}`")
                
                clean_desc, evidence_b64 = extract_image_and_text(t['description'])
                st.markdown(f"**Issue Description:** {clean_desc}")
                
                if evidence_b64:
                    try:
                        img_data = base64.b64decode(evidence_b64)
                        st.image(img_data, caption="Submitted Photo Evidence", width=300)
                    except Exception:
                        pass

                st.markdown(f"**Location:** {t['location']}")
                st.markdown(f"**Filed On:** {t['created_at']}")

                # CLOSED-LOOP CITIZEN VERIFICATION & ESCALATION
                if t["status"] in ["Resolved", "Pending Citizen Verification"]:
                    st.divider()
                    st.subheader("🛡️ Citizen Resolution Audit & Closure Verification")
                    st.caption("The municipal authority reported this issue as resolved. Please verify the actual ground situation.")

                    feed_col1, feed_col2 = st.columns([1.5, 1])
                    with feed_col1:
                        rating = st.select_slider(
                            "Rate the quality of work performed:",
                            options=["⭐ Poor / Incomplete", "⭐⭐ Substandard", "⭐⭐⭐ Acceptable", "⭐⭐⭐⭐ Good", "⭐⭐⭐⭐⭐ Outstanding"],
                            value="⭐⭐⭐⭐ Good",
                            key=f"rating_slider_{t['tracking_id']}"
                        )
                        citizen_remarks = st.text_input(
                            "Citizen Remarks / Ground Audit:", 
                            placeholder="e.g. Work verified on site or leak still active...",
                            key=f"remarks_input_{t['tracking_id']}"
                        )

                    with feed_col2:
                        st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                        c_btn1, c_btn2 = st.columns(2)
                        with c_btn1:
                            if st.button("✅ Confirm & Close", type="primary", key=f"close_btn_{t['tracking_id']}", use_container_width=True):
                                close_res = requests.patch(
                                    f"{API_URL}/api/officer/complaints/{t['tracking_id']}/status",
                                    json={"status": "Officially Closed"}
                                )
                                if close_res.status_code == 200:
                                    st.toast("Grievance officially closed by citizen!", icon="🎉")
                                    st.rerun()
                        with c_btn2:
                            if st.button("🚨 Reopen (Not Fixed)", key=f"reopen_btn_{t['tracking_id']}", use_container_width=True):
                                reopen_res = requests.patch(
                                    f"{API_URL}/api/officer/complaints/{t['tracking_id']}/status",
                                    json={"status": "Reopened & Escalated (P1)"}
                                )
                                if reopen_res.status_code == 200:
                                    st.toast("Ticket Reopened & Escalated to Zonal Authority!", icon="⚠️")
                                    st.rerun()

                elif t["status"] == "Officially Closed":
                    st.success("🏆 This ticket has been verified and officially closed by the citizen.")
                elif "Reopened" in t["status"]:
                    st.error("🚨 This ticket was reopened by the citizen due to incomplete field work and is under expedited escalation review.")
            else:
                st.error("Tracking ID not found.")
        except Exception as e:
            st.error(f"Error contacting API: {e}")

# ----------------------------------------------------
# 3. OFFICER / ADMIN DASHBOARD
# ----------------------------------------------------
elif menu == "Officer / Admin Dashboard":
    st.header("🛡️ Departmental Triage & Nodal Officer Console")
    
    if "is_authenticated" not in st.session_state:
        st.session_state["is_authenticated"] = False
    if "officer_user" not in st.session_state:
        st.session_state["officer_user"] = "officer"
    if "officer_pin" not in st.session_state:
        st.session_state["officer_pin"] = "admin123"

    if not st.session_state["is_authenticated"]:
        st.subheader("🔒 Municipal Nodal Officer Access")
        st.caption("Restricted role-based console for authorized municipal triage personnel.")
        
        login_col1, login_col2 = st.columns([1.2, 1])
        with login_col1:
            input_user = st.text_input("Officer ID / Username", key="login_username")
            input_pass = st.text_input("Access PIN / Password", type="password", key="login_password")
            
            btn_login, btn_recovery = st.columns([1, 1])
            with btn_login:
                if st.button("🔐 Login to Console", type="primary", use_container_width=True):
                    if input_user == st.session_state["officer_user"] and input_pass == st.session_state["officer_pin"]:
                        st.session_state["is_authenticated"] = True
                        st.toast("Authorized Session Initialized", icon="🔑")
                        st.rerun()
                    else:
                        st.error("Invalid credentials entered.")
            
            with btn_recovery:
                show_recovery = st.checkbox("Forgot Credentials?")

            if show_recovery:
                st.info("ℹ️ **Officer Credential Recovery Verification**")
                st.caption("Enter registered municipal security key (`GOV-SEC-2026`) to retrieve credentials.")
                sec_key = st.text_input("Security Recovery Token", type="password", placeholder="e.g. GOV-SEC-2026")
                
                if st.button("Verify & Retrieve Credentials"):
                    if sec_key == "GOV-SEC-2026":
                        st.success(
                            f"✅ Verified Nodal Officer Identity!\n\n"
                            f"**Username:** `{st.session_state['officer_user']}`\n\n"
                            f"**Password:** `{st.session_state['officer_pin']}`"
                        )
                    else:
                        st.error("Invalid recovery token.")

        st.stop()

    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.success(f"🟢 Active Session: Authorized Nodal Officer (`{st.session_state['officer_user']}`)")
    with header_col2:
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state["is_authenticated"] = False
            st.rerun()

    try:
        res = requests.get(f"{API_URL}/api/officer/complaints")
        if res.status_code == 200:
            tickets = res.json()
            if not tickets:
                st.info("No complaints registered yet.")
            else:
                df = pd.DataFrame(tickets)
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Total Complaints", len(df))
                k2.metric("Critical Hazards (P1)", len(df[df['priority_level'] == 'P1']))
                k3.metric("Resolved Cases", len(df[df['status'].isin(['Resolved', 'Officially Closed'])]))
                k4.metric("Linked Duplicates", len(df[df['status'] == 'Duplicate Linked']))
                
                st.divider()
                st.subheader("📊 Operational Analytics & Distribution")
                
                chart_col1, chart_col2 = st.columns(2)
                with chart_col1:
                    dept_df = df['predicted_department'].value_counts().reset_index()
                    dept_df.columns = ['Department', 'Count']
                    fig_dept = px.bar(
                        dept_df,
                        x='Count',
                        y='Department',
                        orientation='h',
                        title="Complaints by Department",
                        color='Department',
                        text='Count'
                    )
                    fig_dept.update_layout(
                        showlegend=False,
                        yaxis={'categoryorder': 'total ascending'},
                        margin=dict(l=20, r=20, t=40, b=20),
                        height=280
                    )
                    st.plotly_chart(fig_dept, use_container_width=True)
                    
                with chart_col2:
                    prio_df = df['priority_level'].value_counts().reset_index()
                    prio_df.columns = ['Priority', 'Count']
                    color_map = {'P1': '#ef4444', 'P2': '#f59e0b', 'P3': '#3b82f6', 'P4': '#10b981'}
                    fig_prio = px.bar(
                        prio_df,
                        x='Count',
                        y='Priority',
                        orientation='h',
                        title="Urgency Priority Breakdown",
                        color='Priority',
                        color_discrete_map=color_map,
                        text='Count'
                    )
                    fig_prio.update_layout(
                        showlegend=False,
                        yaxis={'categoryorder': 'total ascending'},
                        margin=dict(l=20, r=20, t=40, b=20),
                        height=280
                    )
                    st.plotly_chart(fig_prio, use_container_width=True)

                st.divider()

                # GIS Hotspot Map (OpenStreetMap)
                st.subheader("🗺️ Live Municipal Incident Hotspot Map")
                st.caption("Real-time geographic distribution across municipal wards.")

                map_records = []
                for loc, coords in WARD_COORDINATES.items():
                    ward_complaints = df[df['location'] == loc]
                    count = len(ward_complaints)
                    p1_hazards = len(ward_complaints[ward_complaints['priority_level'] == 'P1'])
                    display_size = max(count * 6 + 14, 18)

                    map_records.append({
                        "Ward": loc,
                        "lat": coords["lat"],
                        "lon": coords["lon"],
                        "Active Incidents": count,
                        "Critical Hazards": p1_hazards,
                        "Marker Size": display_size
                    })

                map_df = pd.DataFrame(map_records)

                fig_map = px.scatter_mapbox(
                    map_df,
                    lat="lat",
                    lon="lon",
                    size="Marker Size",
                    color="Ward",
                    color_discrete_map=WARD_COLOR_PALETTE,
                    size_max=32,
                    zoom=11,
                    hover_name="Ward",
                    hover_data={
                        "Active Incidents": True, 
                        "Critical Hazards": True, 
                        "Marker Size": False,
                        "lat": False, 
                        "lon": False,
                        "Ward": False
                    },
                    mapbox_style="open-street-map",
                    title="Municipal Wards: Sector Overview"
                )
                fig_map.update_layout(
                    margin=dict(l=0, r=0, t=35, b=0),
                    height=380,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_map, use_container_width=True)

                st.divider()

                # Action Bar: Real-time Filters & Data Export
                st.subheader("📋 Active Incident Feed & Live Triage")
                
                fil_col1, fil_col2, fil_col3 = st.columns([1.5, 1.5, 1])
                with fil_col1:
                    dept_filter = st.selectbox("Filter by Department", ["All Departments"] + sorted(list(df['predicted_department'].unique())))
                with fil_col2:
                    prio_filter = st.selectbox("Filter by Urgency", ["All Priorities", "P1", "P2", "P3", "P4"])
                with fil_col3:
                    st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Export CSV",
                        data=csv_data,
                        file_name=f"grievance_audit_log_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                filtered_tickets = tickets
                if dept_filter != "All Departments":
                    filtered_tickets = [t for t in filtered_tickets if t["predicted_department"] == dept_filter]
                if prio_filter != "All Priorities":
                    filtered_tickets = [t for t in filtered_tickets if t["priority_level"] == prio_filter]

                st.caption(f"Showing **{len(filtered_tickets)}** matching records")

                # Officer Ticket Loop
                status_options = [
                    "Pending", 
                    "In Progress", 
                    "Resolved", 
                    "Pending Citizen Verification", 
                    "Officially Closed", 
                    "Duplicate Linked",
                    "Reopened & Escalated (P1)"
                ]

                for t in filtered_tickets:
                    badge_color = "🔴" if t["priority_level"] == "P1" else ("🟡" if t["priority_level"] == "P2" else "🟢")
                    sla_status, is_breached = calculate_sla(t['created_at'], t['priority_level'], t['status'])
                    
                    title = f"{badge_color} [{t['tracking_id']}] {t['predicted_department']} | Priority: {t['priority_level']} | Status: {t['status']}"
                    if t.get("is_duplicate"):
                        title += f" [DUPLICATE of {t.get('parent_ticket_id')}]"
                    if is_breached:
                        title += " ⚠️ [OVERDUE]"
                        
                    with st.expander(title):
                        clean_desc, evidence_b64 = extract_image_and_text(t['description'])
                        st.write(f"**Description:** {clean_desc}")
                        
                        if evidence_b64:
                            try:
                                img_data = base64.b64decode(evidence_b64)
                                st.markdown("🖼️ **Citizen Submitted Visual Evidence:**")
                                st.image(img_data, width=320)
                            except Exception:
                                st.caption("*(Attached image format unreadable)*")

                        st.markdown(
                            f"""
                            <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">
                                📍 <b>Incident Coordinates:</b> Lat: {WARD_COORDINATES.get(t['location'], {}).get('lat', 'N/A')}, Lon: {WARD_COORDINATES.get(t['location'], {}).get('lon', 'N/A')}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.write(f"**Ward:** {t['location']} | **Citizen:** {t['citizen_name']} ({t['citizen_phone']})")
                        st.write(f"**AI Confidence:** {int(t['confidence_score'] * 100)}% | **Similarity:** {int(t.get('similarity_score', 0) * 100)}%")
                        st.markdown(f"**Target Resolution SLA:** `{sla_status}`")
                        
                        sop = get_action_recommendation(t['predicted_department'], t['priority_level'])
                        st.markdown(
                            f"""
                            <div style="background: rgba(255, 255, 255, 0.03); border-left: 4px solid #3b82f6; padding: 10px 14px; border-radius: 6px; margin: 10px 0;">
                                <span style="font-weight: 600; color: #93c5fd; font-size: 0.95rem;">🛠️ AI Field Action Plan & SOP Dispatch:</span><br>
                                <span style="font-size: 0.9rem;"><b>• Standard Action:</b> {sop['action']}</span><br>
                                <span style="font-size: 0.9rem;"><b>• Required Crew:</b> {sop['crew']}</span><br>
                                <span style="font-size: 0.9rem;"><b>• Equipment Allocation:</b> {sop['equipment']}</span><br>
                                <span style="font-size: 0.85rem; color: #fbbf24;"><b>⚠️ Operational Caution:</b> {sop['safety_note']}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        col_stat, col_btn = st.columns([4, 1])
                        with col_stat:
                            current_idx = status_options.index(t["status"]) if t["status"] in status_options else 0
                            new_status = st.selectbox(
                                "Update Status", 
                                status_options, 
                                index=current_idx,
                                key=f"sel_{t['tracking_id']}"
                            )
                        with col_btn:
                            st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                            if st.button("Update", key=f"btn_{t['tracking_id']}", use_container_width=True):
                                update_res = requests.patch(
                                    f"{API_URL}/api/officer/complaints/{t['tracking_id']}/status",
                                    json={"status": new_status}
                                )
                                if update_res.status_code == 200:
                                    st.session_state[f"last_sms_{t['tracking_id']}"] = {
                                        "phone": t["citizen_phone"],
                                        "status": new_status,
                                        "dept": t["predicted_department"]
                                    }
                                    st.toast(f"Updated {t['tracking_id']} to {new_status}!", icon="✅")
                                    st.rerun()

                        if f"last_sms_{t['tracking_id']}" in st.session_state:
                            sms_meta = st.session_state[f"last_sms_{t['tracking_id']}"]
                            render_sms_dispatch_card(
                                sms_meta["phone"], 
                                t["tracking_id"], 
                                sms_meta["dept"], 
                                sms_meta["status"]
                            )
        else:
            st.error("Failed to load complaints.")
    except Exception as e:
        st.error(f"Error: {e}")