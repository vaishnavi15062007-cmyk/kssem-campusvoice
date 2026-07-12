import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. Set up professional wide screen dashboard view (MUST BE AT VERY TOP)
st.set_page_config(page_title="CampusVoice - KSSEM", layout="wide")

# --- AUTHENTICATION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# --- SMART USN DEPARTMENT DETECTOR ---
def get_dept_from_usn(usn):
    if "AD" in usn: return "AI&DS"
    if "CS" in usn: return "CSE"
    if "EC" in usn: return "ECE"
    if "CB" in usn: return "CSBS"
    if "ME" in usn: return "Mechanical"
    if "CV" in usn: return "Civil"
    return "All"

# --- THE SIMULATED AI BRAIN ---
def predict_priority_ai(title, description):
    text = f"{title} {description}".lower()
    urgent_words = ["urgent", "emergency", "immediate", "fire", "police", "ambulance", "ragging", "harassment", "bleeding", "hazard", "assault"]
    high_words = ["stale", "poison", "cheating", "stolen", "theft", "missing", "leak", "broken", "not working", "fail", "exam", "hygiene"]
    medium_words = ["dirty", "unhygienic", "torn", "damage", "slow", "noise", "wifi", "network", "repair"]
    
    if any(word in text for word in urgent_words): return "Urgent"
    if any(word in text for word in high_words): return "High"
    if any(word in text for word in medium_words): return "Medium"
    return "Low"
# ------------------------------

# 2. Central shared database memory
if "mock_db" not in st.session_state:
    st.session_state.mock_db = [
        {"id": "CV-101", "usn": "1KG25AD103", "dept": "AI&DS", "category": "Campus Infrastructure & Hygiene - Washrooms", "title": "WASHROOM ISSUE", "desc": "URGENT CLEANING REQUIRED", "priority": "High", "status": "Pending", "submitter": "Anonymous", "feedback": ""},
        {"id": "CV-102", "usn": "1KG25EC051", "dept": "ECE", "category": "Academic - Faculty Behavior", "title": "ragging", "desc": "Seniors misbehavior near labs", "priority": "Urgent", "status": "Pending", "submitter": "Anonymous", "feedback": ""},
        {"id": "CV-107", "usn": "1KG25AD102", "dept": "AI&DS", "category": "Campus Infrastructure & Hygiene - Lab Equipment", "title": "Survey lab equipment error", "desc": "The auto levels are showing calibration errors during practical hours.", "priority": "Medium", "status": "Resolved", "submitter": "1KG25AD102", "feedback": "Resolved quickly by lab admin. 5/5 Stars."},
        {"id": "CV-108", "usn": "ADMIN101", "dept": "MBA", "category": "Library - Book Availability", "title": "Business module notes missing", "desc": "Reference text materials for management economics are unavailable in the library.", "priority": "Low", "status": "Resolved", "submitter": "Anonymous", "feedback": "Books restocked. 4/5 Stars."}
    ]

if "my_session_ids" not in st.session_state:
    st.session_state.my_session_ids = ["CV-107"] 

# 3. Custom CSS theme injection rules
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
    
    .brand-container { padding: 5px 0px; margin-bottom: 10px; text-align:center;}
    .brand-icon { font-size: 32px; margin-bottom: 4px; display: block; }
    .brand-name { color: #1E293B; font-weight: 800; font-size: 22px; display: block; font-family: 'Inter', sans-serif; }
    .brand-sub { color: #64748B; font-size: 11px; font-weight: 600; margin-top: 4px; letter-spacing: 0.5px; text-transform: uppercase; }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-of-type { display: none !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label { padding: 10px 15px; border-radius: 8px; background-color: transparent; margin-bottom: 5px; cursor: pointer; transition: all 0.2s ease-in-out; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover { background-color: #F1F5F9; }

    .datetime-badge { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 16px; text-align: right; font-family: 'Inter', sans-serif; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }
    .datetime-date { font-size: 14px; font-weight: 700; color: #1E293B; }
    .datetime-time { font-size: 12px; font-weight: 500; color: #64748B; margin-top: 2px; }

    .pastel-purple { background-color: #F3E8FF; border: 1px solid #E9D5FF; border-radius: 12px; padding: 20px; }
    .pastel-blue { background-color: #E0F2FE; border: 1px solid #BAE6FD; border-radius: 12px; padding: 20px; }
    .pastel-pink { background-color: #FCE7F3; border: 1px solid #FBCFE8; border-radius: 12px; padding: 20px; }
    .pastel-green { background-color: #DCFCE7; border: 1px solid #BBF7D0; border-radius: 12px; padding: 20px; }
    .m-title { font-size: 12px; font-weight: 700; text-transform: uppercase; color: #475569; }
    .m-value { font-size: 28px; font-weight: 800; color: #1E293B; }
    
    .data-row { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; margin-bottom: 10px; }
    
    .login-box { max-width: 400px; margin: 50px auto; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# LOGIN SCREEN
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center; margin-top:40px;'><span style='font-size:80px; line-height:1;'>🎓</span><h1 style='color:#1E293B; font-weight:800; margin-top:10px;'>CampusVoice</h1><p style='color:#64748B;'>K.S. School of Engineering and Management</p></div>", unsafe_allow_html=True)
    
    st.write("") 
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h3 style='text-align:center; margin-bottom: 0px;'>🔐 Login</h3>", unsafe_allow_html=True)
            st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True) 
            
            login_usn = st.text_input("Enter your USN or Admin ID:", placeholder="e.g. 1KG25XXXXX or ADMIN123").strip().upper()
            
            st.write("")
            if st.button("Access Portal →", type="primary", use_container_width=True):
                if login_usn.startswith("1KG2") and len(login_usn) >= 9:
                    st.session_state.logged_in = True
                    st.session_state.current_user = {
                        "usn": login_usn,
                        "dept": get_dept_from_usn(login_usn),
                        "role": "Student"
                    }
                    st.rerun()
                elif login_usn.startswith("ADMIN") and len(login_usn) > 5:
                    st.session_state.logged_in = True
                    st.session_state.current_user = {
                        "usn": login_usn,
                        "dept": "All",
                        "role": "Admin"
                    }
                    st.rerun()
                else:
                    st.error("❌ Invalid ID format. (Must start with '1KG2' or 'ADMIN' followed by your number)")
            
            st.markdown("<br><small style='color:#94A3B8; text-align:center; display:block;'>Students: Enter your KSSEM USN.<br>Faculty: Enter your Admin ID (e.g. ADMIN123).</small>", unsafe_allow_html=True)
        
    st.stop() 

# ==========================================
# MAIN APP PORTALS
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="brand-container" style="text-align:left;">
        <div><span class="brand-icon" style="font-size:24px; display:inline-block;">🎓</span><span class="brand-name" style="display:inline-block; font-size:20px;">CampusVoice</span></div>
        <div class="brand-sub">KSSEM Portal</div>
    </div>
    """, unsafe_allow_html=True)
    
    role_color = "#1D4ED8" if st.session_state.current_user['role'] == "Student" else "#9F1239"
    role_bg = "#DBEAFE" if st.session_state.current_user['role'] == "Student" else "#FFE4E6"
    
    st.markdown(f"""
    <div style="background-color:#F1F5F9; padding:10px; border-radius:8px; margin:10px 0;">
        <small style="color:#64748B; text-transform:uppercase; font-weight:700;">Logged in as</small><br>
        <span style="color:{role_color}; font-size:16px; font-weight:bold; background:{role_bg}; padding:4px 8px; border-radius:6px; display:inline-block; margin-top:4px;">{st.session_state.current_user['usn']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    if st.session_state.current_user['role'] == "Admin":
        menu_options = ["📊 Dashboard", "🔍 Faculty Review Portal"]
    else:
        menu_options = ["📊 Dashboard", "📋 My Complaints", "📝 Submit Complaint", "📜 Policies"]
        
    page = st.radio("Navigation Menu", menu_options, label_visibility="collapsed")
    
    st.write("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

df = pd.DataFrame(st.session_state.mock_db)
DEPARTMENTS = ["All", "CSE", "ECE", "AI&DS", "CSBS", "Mechanical", "Civil", "MBA"]

# --- ROUTING VIEW PANELS ---

if page == "📊 Dashboard":
    now = datetime.now()
    current_date = now.strftime("%A, %B %d, %Y")
    current_time = now.strftime("%I:%M %p")
    
    head_left, head_right = st.columns([3, 1])
    with head_left:
        st.markdown("<h1 style='color:#1E293B; font-weight:800; margin-bottom:0px;'>Dashboard</h1><p style='color:#64748B;'>Overview of all campus complaints and real-time tracking</p>", unsafe_allow_html=True)
    with head_right:
        st.markdown(f"""
        <div class="datetime-badge">
            <div class="datetime-date">🗓️ {current_date}</div>
            <div class="datetime-time">🕒 System Time: {current_time}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("---")
    
    total_c, pending_c, progress_c, resolved_c = len(df), len(df[df['status'] == 'Pending']), len(df[df['status'] == 'In Progress']), len(df[df['status'] == 'Resolved'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f'<div class="pastel-purple"><div class="m-title">Total Complaints</div><div class="m-value">{total_c}</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="pastel-blue"><div class="m-title">Pending Action</div><div class="m-value">{pending_c}</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="pastel-pink"><div class="m-title">In Progress</div><div class="m-value">{progress_c}</div></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="pastel-green"><div class="m-title">Resolved Issues</div><div class="m-value" style="color:#15803D;">{resolved_c}</div></div>', unsafe_allow_html=True)
        
    st.write("---")
    
    # CENTERED PIE CHART SECTION
    st.markdown("<h3 style='text-align: center;'>📊 Department-wise Distribution</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 14px;'>Total volume of active tickets tracked per branch channel</p>", unsafe_allow_html=True)

    spacer_left, chart_mid, spacer_right = st.columns([1, 2, 1])
    with chart_mid:
        branch_counts = df['dept'].value_counts().reset_index()
        branch_counts.columns = ['Department', 'Complaints Count']
        
        fig = px.pie(branch_counts, names='Department', values='Complaints Count', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.write("---")

    # URGENT QUEUE SECTION 
    st.markdown("### 🚨 Urgent Attention Queue")
    st.caption("Active high severity alerts requiring immediate intervention")
    
    urgent_df = df[df['priority'].isin(['High', 'Urgent'])]
    if urgent_df.empty:
        st.success("Clear queue! No immediate urgent hazards logged.")
    else:
        for idx, row in urgent_df.iterrows():
            color = "#9F1239" if row['priority'] == "Urgent" else "#C2410C"
            bg_color = "#FFE4E6" if row['priority'] == "Urgent" else "#FFEDD5"
            st.markdown(f"""
            <div style="background-color:#FFF1F2; border-left:5px solid #F43F5E; padding:12px 14px; border-radius:8px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; font-weight:700;">
                    <span style="color:#1E293B;">{row['title']}</span>
                    <span style="color:{color}; background-color:{bg_color}; padding:1px 6px; border-radius:4px; font-size:11px;">{row['priority']}</span>
                </div>
                <p style="color:#475569; font-size:13px; margin:4px 0;">{row['desc']}</p>
                <small style="color:#64748B;">Department: <strong>{row['dept']}</strong></small>
            </div>
            """, unsafe_allow_html=True)


# ----------------- STUDENT ONLY PAGES -----------------
elif page == "📋 My Complaints":
    st.markdown("<h1 style='color:#1E293B; font-weight:800; margin-bottom:0px;'>My Complaints</h1><p style='color:#64748B;'>Track the real-time status of your submitted grievances</p>", unsafe_allow_html=True)
    st.write("---")
    
    my_df = df[df['usn'] == st.session_state.current_user['usn']]
    
    if my_df.empty:
        st.info("You haven't submitted any complaints to the system yet.")
    else:
        for idx, row in my_df.iterrows():
            p_colors = {"Urgent": "#991B1B", "High": "#9A3412", "Medium": "#1E40AF", "Low": "#15803D"}
            s_colors = {"Pending": "#64748B", "In Progress": "#0284C7", "Resolved": "#16A34A"}
            
            p_color = p_colors.get(row['priority'], "#475569")
            s_color = s_colors.get(row['status'], "#475569")
            
            # Removed the Ticket ID from the Student view
            st.markdown(f"""
            <div class="data-row">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <small style="color:#64748B;">{row['category']} → {row['dept']}</small>
                    <div>
                        <span style="color:{p_color}; border:1px solid {p_color}; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold; margin-right:5px;">● {row['priority']}</span>
                        <span style="background-color:#F1F5F9; color:{s_color}; padding:2px 8px; border-radius:6px; font-size:12px; font-weight:bold;">{row['status']}</span>
                    </div>
                </div>
                <h4 style="margin:0px 0 8px 0; color:#1E293B;">{row['title']}</h4>
                <p style="color:#475569; font-size:14px; margin-bottom:12px;">{row['desc']}</p>
                <div style="display:flex; justify-content:space-between;">
                    <small style="color:#94A3B8;">Submitter: {row['submitter']}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if row['status'] == "Resolved" and row['feedback']:
                st.markdown(f"<div style='background-color:#F0FDF4; padding:10px; border-radius:8px; font-size:13px; color:#166534; margin-top:-5px; margin-bottom:15px;'><strong>Your Feedback:</strong> {row['feedback']}</div>", unsafe_allow_html=True)

elif page == "📝 Submit Complaint":
    st.markdown("<h2 style='color:#1E293B; font-weight:800; margin-bottom:0px;'>Submit a Complaint</h2><p style='color:#64748B; margin-top:0px;'>Tell us about your concern securely.</p>", unsafe_allow_html=True)
    
    issue_categories = {
        "Academic": ["Attendance", "Exams & Grading", "Faculty Behavior", "Lab Equipment", "Syllabus Completion", "Project Guidance", "Other"],
        "Hostel": ["Room Maintenance", "Washroom Hygiene", "Wi-Fi & Internet", "Water Supply", "Security & Curfew", "Laundry", "Other"],
        "Canteen": ["Food Quality", "Unhygienic Conditions", "Menu Pricing", "Seating Availability", "Staff Behavior", "Other"],
        "Library": ["Book Availability", "Digital Subscriptions", "Reading Room Environment", "Fines & Renewals", "System/PC Issues", "Other"],
        "Sports & Facilities": ["Equipment Damage", "Ground Maintenance", "Timings & Access", "First Aid Availability", "Other"],
        "Campus Infrastructure & Hygiene": ["General Washrooms", "Classroom Benches & Fans", "Elevator Issues", "Parking", "Drinking Water Filters", "Other"]
    }

    if "form_step" not in st.session_state: st.session_state.form_step = 1
    if "temp_title" not in st.session_state: st.session_state.temp_title = ""
    if "temp_desc" not in st.session_state: st.session_state.temp_desc = ""
    if "temp_dept" not in st.session_state: st.session_state.temp_dept = st.session_state.current_user["dept"]
    if "temp_cat" not in st.session_state: st.session_state.temp_cat = ""
    if "temp_priority" not in st.session_state: st.session_state.temp_priority = "Low"
    if "is_anonymous" not in st.session_state: st.session_state.is_anonymous = True

    st.markdown(f"<span style='background-color:#F3E8FF; color:#6B21A8; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700;'>Step {st.session_state.form_step} of 3</span>", unsafe_allow_html=True)
    st.write("")

    if st.session_state.form_step == 1:
        st.session_state.temp_dept = st.selectbox("Select your engineering branch:", DEPARTMENTS[1:], index=DEPARTMENTS[1:].index(st.session_state.temp_dept) if st.session_state.temp_dept in DEPARTMENTS[1:] else 0)
        st.session_state.is_anonymous = st.checkbox("Submit Anonymously (Hide my identity from administration)", value=st.session_state.is_anonymous)
        
        st.write("---")
        st.markdown("#### Categorize Your Issue")
        selected_main = st.selectbox("1. Main Category:", list(issue_categories.keys()))
        selected_sub = st.selectbox("2. Specific Sub-category:", issue_categories[selected_main])
        
        st.write("---")
        if st.button("Next: Add Details →", type="primary"):
            st.session_state.temp_cat = f"{selected_main} - {selected_sub}"
            st.session_state.form_step = 2
            st.rerun()

    elif st.session_state.form_step == 2:
        st.markdown("#### Describe Your Issue")
        st.info(f"Filing under: **{st.session_state.temp_dept}** | Category: **{st.session_state.temp_cat}**")
        
        st.session_state.temp_title = st.text_input("Complaint Title", value=st.session_state.temp_title, placeholder="e.g. Broken bench in room 204")
        st.session_state.temp_desc = st.text_area("Detailed Description", value=st.session_state.temp_desc, placeholder="Explain the issue in your own words...")
        
        st.write("---")
        b1, b2 = st.columns([1, 5])
        if b1.button("← Back"):
            st.session_state.form_step = 1
            st.rerun()
        if b2.button("Analyze with AI 🪄", type="primary"):
            if st.session_state.temp_title.strip() == "": 
                st.error("Title cannot be blank!")
            else:
                st.session_state.form_step = 3
                st.rerun()

    elif st.session_state.form_step == 3:
        st.markdown("### Automated Priority & Duplicate Verification")
        
        st.session_state.temp_priority = predict_priority_ai(st.session_state.temp_title, st.session_state.temp_desc)
        is_duplicate = any(st.session_state.temp_title.lower().strip() == x['title'].lower().strip() for x in st.session_state.mock_db)
        
        p_colors = {"Urgent": ("#FEE2E2", "#991B1B"), "High": ("#FFEDD5", "#9A3412"), "Medium": ("#DBEAFE", "#1E40AF"), "Low": ("#DCFCE7", "#15803D")}
        bg, text_c = p_colors.get(st.session_state.temp_priority, ("#DCFCE7", "#15803D"))
        
        st.markdown(f"""
        <div style="background-color:#EFF6FF; border:1px solid #BFDBFE; border-radius:12px; padding:16px; margin-bottom:12px;">
            <span style="color:#1D4ED8; font-weight:700;">🎓 AI Priority Detection:</span> 
            <span style="background-color:{bg}; color:{text_c}; padding:4px 12px; border-radius:10px; font-size:12px; font-weight:bold; text-transform:uppercase;">{st.session_state.temp_priority} PRIORITY</span>
            <p style="margin-top:8px; font-size:13px; color:#475569;">The AI scanned your text for urgency keywords to route this ticket automatically to administration.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if is_duplicate:
            st.markdown("""
            <div style="background-color: #FFF7ED; border: 1px solid #FFEDD5; border-radius: 12px; padding: 16px; margin-bottom: 24px;">
                <span style="color:#C2410C; font-weight:700;">⚠️ Possible Duplicate Detected:</span><br>
                <small style="color:#9A3412;">A highly identical issue already exists in database queue records.</small>
            </div>
            """, unsafe_allow_html=True)
            
        b1, b2 = st.columns([1, 5])
        if b1.button("← Edit"): st.session_state.form_step = 2; st.rerun()
        if b2.button("Submit Final Complaint ✔️", type="primary"):
            new_id = f"CV-{101 + len(st.session_state.mock_db)}"
            submitter_name = "Anonymous" if st.session_state.is_anonymous else st.session_state.current_user["usn"]
            
            st.session_state.mock_db.append({
                "id": new_id,
                "usn": st.session_state.current_user["usn"],
                "dept": st.session_state.temp_dept, 
                "category": st.session_state.temp_cat, 
                "title": st.session_state.temp_title, 
                "desc": st.session_state.temp_desc, 
                "priority": st.session_state.temp_priority,
                "status": "Pending",
                "submitter": submitter_name,
                "feedback": ""
            })
            st.session_state.my_session_ids.append(new_id)
            
            st.balloons()
            st.success(f"🎉 Complaint successfully logged!")
            st.session_state.temp_title = ""
            st.session_state.temp_desc = ""
            st.session_state.temp_priority = "Low"
            st.session_state.is_anonymous = True
            st.session_state.form_step = 1
            st.rerun()

elif page == "📜 Policies":
    st.markdown("<h1 style='color:#1E293B; font-weight:800; margin-bottom:0px;'>Policies & Code of Conduct</h1><p style='color:#64748B;'>Official guidelines, rules, and behavioral expectations for all students at KSSEM.</p>", unsafe_allow_html=True)
    st.write("---")

    st.markdown("### 📚 Academic Rules & Evaluation")
    st.info("Failure to comply with academic policies may result in detainment from semester exams.")
    st.markdown("""
    * **Attendance Requirement:** A minimum of **75% attendance** is strictly mandatory in every theory and practical subject to be eligible for final exams.
    * **Internal Assessments (IA):** Absence from internal exams without a valid medical certificate and prior HoD approval will result in a zero mark. No re-tests will be conducted for unexcused absences.
    * **Punctuality:** Students must be seated in classrooms 5 minutes before the lecture begins. Latecomers will be marked absent for the session.
    * **Lab Records:** Practical observation books and lab records must be updated, diagrammatically neat, and signed by the respective faculty before entering the next lab session.
    * **Project Submissions:** Mini-projects and final semester project phases must strictly adhere to the deadlines set by the evaluation committee. Late submissions incur a 10% penalty per day.
    * **Academic Integrity:** Plagiarism in assignments, project reports, or malpractice during examinations will lead to immediate confiscation of the paper and semester suspension.
    """)
    st.write("---")

    st.markdown("### 🚫 Anti-Ragging & Behavioral Conduct")
    st.error("Ragging is a criminal offense. Zero Tolerance Policy in effect.")
    st.markdown("""
    * **Anti-Ragging Act:** Ragging in any form (physical, verbal, or psychological) is strictly prohibited. Offenders will face immediate expulsion, FIR registration, and handover to local police.
    * **Dress Code:** Students are expected to wear decent, professional attire. Specific lab uniforms (aprons, closed shoes) must be worn during mechanical, civil, and chemistry practical sessions.
    * **ID Cards:** Campus ID cards must be worn around the neck at all times. Entry to the library, exam halls, and computer labs will be denied without a valid ID.
    * **Mobile Phones:** The use of mobile phones inside classrooms and labs is strictly prohibited unless permitted by the faculty for academic purposes. Confiscated phones will only be returned at the end of the semester.
    * **Social Media Conduct:** Posting defamatory content about the institution, faculty, or peers on social media platforms will invite strict disciplinary action.
    * **Classroom Decorum:** Eating, drinking, or engaging in disruptive conversations during lectures is strictly forbidden.
    """)
    st.write("---")

    st.markdown("### 🏢 Hostel, Mess & Campus Life")
    st.warning("Hostel rules apply to all boarders 24/7.")
    st.markdown("""
    * **Curfew Timings:** All hostel residents must return to the campus gates by **7:30 PM**. Late entries require prior written permission from the local guardian and the Hostel Warden.
    * **Guest Policy:** Day scholars and external guests are not allowed inside hostel rooms. Visitors may only be met in the designated visitor lounge during permitted hours.
    * **Mess Etiquette:** Wastage of food is strictly discouraged. Utensils must not be taken out of the dining hall under any circumstances.
    * **Substance Policy:** Consumption or possession of alcohol, tobacco, e-cigarettes, or illegal substances on campus or in the hostel is strictly banned and will result in immediate expulsion.
    * **Property Damage:** Defacing walls, breaking furniture, or damaging campus property will result in heavy fines levied on the responsible individual or the entire floor.
    * **Quiet Hours:** Mandatory quiet hours are observed from 10:00 PM to 6:00 AM to ensure a conducive studying and sleeping environment.
    """)
    st.write("---")

    st.markdown("### 💻 IT, Library & Infrastructure")
    st.success("Utilize campus resources responsibly.")
    st.markdown("""
    * **Wi-Fi Usage:** Campus internet is monitored and provided exclusively for educational purposes. Accessing inappropriate sites, gaming, or unauthorized torrenting will result in a permanent MAC address ban.
    * **Computer Labs:** Do not install unauthorized software, alter system settings, or unplug hardware in the programming labs. Always log out of your session before leaving the terminal.
    * **Hardware Damage:** Students handling microcontrollers, sensors, or expensive lab equipment will be held financially responsible for damages caused by negligence.
    * **Library Rules:** Strict silence must be maintained. Books returned after the due date will incur a daily fine. Reference materials and journals cannot be taken outside the reading room.
    * **Parking:** Student vehicles must be parked only in the designated student parking lots. Speeding or reckless driving on campus roads will result in the suspension of parking privileges.
    """)
    st.write("---")

    st.markdown("### 🛡️ Campus Security & Health Protocols")
    st.info("Security personnel have the authority to check IDs and bags at any time.")
    st.markdown("""
    * **Gate Pass System:** Hostellers leaving the campus during non-curfew hours must generate a digital gate pass approved by their local guardian and the respective warden.
    * **Visitor Policy:** No external visitors (including alumni) are allowed past the main reception area without prior physical authorization from the administration block.
    * **Night Movement:** Roaming around academic blocks, lab corridors, or sports grounds after **9:00 PM** is strictly prohibited unless authorized for a specific college event.
    * **Medical Leave:** Any leave exceeding 3 days requires a certified medical document from a registered hospital and sign-off from the Chief Medical Officer to excuse attendance.
    * **Emergencies:** In case of severe injury or illness, the campus ambulance must be contacted immediately via the warden or main security desk.
    """)

# ----------------- ADMIN/FACULTY ONLY PAGES -----------------
elif page == "🔍 Faculty Review Portal":
    st.markdown("<h1 style='color:#1E293B; font-weight:800; margin-bottom:0px;'>Faculty Review Portal</h1><p style='color:#64748B;'>Administrative dashboard to examine, prioritize, and filter campus issues.</p>", unsafe_allow_html=True)
    
    st.markdown("### 🔍 Search Matrix Filters")
    s_col1, s_col2, s_col3 = st.columns([2, 1, 1])
    search_query = s_col1.text_input("Search content keywords or titles:", placeholder="Type keywords...")
    dept_filter = s_col2.selectbox("Filter Department:", DEPARTMENTS)
    status_filter = s_col3.selectbox("Filter Status:", ["All", "Pending", "In Progress", "Resolved"])
        
    filtered_df = df.copy()
    if search_query: filtered_df = filtered_df[filtered_df['title'].str.contains(search_query, case=False) | filtered_df['desc'].str.contains(search_query, case=False)]
    if dept_filter != "All": filtered_df = filtered_df[filtered_df['dept'] == dept_filter]
    if status_filter != "All": filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
    st.write("---")
    st.markdown(f"#### 📄 Displaying Database Records ({len(filtered_df)} items found)")
    
    if filtered_df.empty:
        st.info("No records found matching those query filter selections.")
    else:
        # Rebuilt this section with native Streamlit elements to allow interactive widgets
        for idx, row in filtered_df.iterrows():
            with st.container(border=True):
                col_text, col_action = st.columns([3, 1])
                
                with col_text:
                    st.markdown(f"<h4 style='margin:0px; color:#1E293B;'>{row['title']}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#475569; font-size:14px; margin:8px 0px;'>{row['desc']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<small style='color:#64748B;'>Dept: <strong>{row['dept']}</strong> | Category: {row['category']} | Submitter: {row['submitter']}</small>", unsafe_allow_html=True)
                
                with col_action:
                    # Colored Priority Badge
                    p_colors = {"Urgent": "#9F1239", "High": "#C2410C", "Medium": "#1D4ED8", "Low": "#15803D"}
                    p_bg = {"Urgent": "#FFE4E6", "High": "#FFEDD5", "Medium": "#DBEAFE", "Low": "#DCFCE7"}
                    st.markdown(f"<div style='margin-bottom:8px;'><span style='color:{p_colors.get(row['priority'], '#000')}; background-color:{p_bg.get(row['priority'], '#fff')}; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold;'>{row['priority']} Priority</span></div>", unsafe_allow_html=True)
                    
                    # The Magic Dropdown Editor for Admins
                    new_status = st.selectbox(
                        "Update Status:",
                        options=["Pending", "In Progress", "Resolved"],
                        index=["Pending", "In Progress", "Resolved"].index(row['status']),
                        key=f"status_update_{row['id']}",
                        label_visibility="collapsed"
                    )
                    
                    # Instantly save the changes and refresh the screen
                    if new_status != row['status']:
                        for i, item in enumerate(st.session_state.mock_db):
                            if item['id'] == row['id']:
                                st.session_state.mock_db[i]['status'] = new_status
                                break
                        st.rerun()