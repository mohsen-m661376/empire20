import streamlit as st
import random
import hashlib
import sqlite3
import time
import pandas as pd
import numpy as np

# --- CONFIGURATION & ASSETS ---
APP_NAME = "NEURO-VIRAL ARCHITECT"
VERSION = "v4.0.0 (Ultimate)"
SECRET_KEY = "X-77-OMEGA-SALT-KEY"
ADMIN_ID = "932654521"

# --- DATABASE MANAGEMENT ---
def init_db():
    conn = sqlite3.connect('empire_users.db')
    c = conn.cursor()
    # Table for licenses
    c.execute('''CREATE TABLE IF NOT EXISTS licenses 
                 (license_key TEXT PRIMARY KEY, username TEXT, hardware_id TEXT, status TEXT)''')
    # Table for user history
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (username TEXT, strategy TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def generate_license_hash(username):
    """Generates a secure hash license based on username"""
    raw = f"{username.lower()}-{SECRET_KEY}"
    return f"EMP-{hashlib.sha256(raw.encode()).hexdigest()[:12].upper()}"

def authenticate(username, key):
    expected_key = generate_license_hash(username)
    if key.strip() == expected_key:
        return True
    return False

def check_license_in_db(username, key):
    conn = sqlite3.connect('empire_users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM licenses WHERE license_key=?", (key,))
    record = c.fetchone()
    
    if record:
        saved_user = record[1]
        conn.close()
        if saved_user.lower() == username.lower():
            return True, "✅ Identity Verified."
        else:
            return False, "⛔ License is locked to another user."
    else:
        # Register new license
        if authenticate(username, key):
            c.execute("INSERT INTO licenses VALUES (?, ?, ?, ?)", (key, username, "UNKNOWN_DEVICE", "ACTIVE"))
            conn.commit()
            conn.close()
            return True, "🚀 Activation Successful. Welcome."
        else:
            conn.close()
            return False, "❌ Invalid License Key."

# --- STRATEGY ENGINE (EXPANDED) ---
STRATEGIES = [
    {"title": "The Pattern Interrupt", "desc": "Start video upside down for 0.5s, then flip automatically.", "score": 94},
    {"title": "ASMR Overlay", "desc": "Layer 'crackle' sounds under your voice at 10% volume. Increases retention.", "score": 89},
    {"title": "The Negative Hook", "desc": "Start with: 'Stop scrolling if you want to save money...'", "score": 92},
    {"title": "Color Theory: Red", "desc": "Wear a red item or use red text. It triggers urgency algorithms.", "score": 88},
    {"title": "Loop Perfection", "desc": "End your sentence with 'and that is why...' which leads back to the start.", "score": 96},
    {"title": "Speed Read", "desc": "Put a long text on screen for only 1 second. Forces users to re-watch/pause.", "score": 91},
    {"title": "Comment Bait", "desc": "Intentionally mispronounce one common word to trigger correction comments.", "score": 85},
    {"title": "POV Shift", "desc": "Tape phone to a moving object (door, fan, car) for a unique perspective.", "score": 93},
    {"title": "The Secret", "desc": "Whisper the most important part of the video.", "score": 87},
    {"title": "Controversy Light", "desc": "State an unpopular opinion about a harmless topic (e.g., 'Pizza is bad').", "score": 90}
]

# --- UI STYLING (MOBILE OPTIMIZED) ---
def apply_style():
    st.markdown("""
    <style>
        /* MAIN THEME */
        .stApp {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            font-family: 'Helvetica Neue', sans-serif;
        }
        /* HIDE DEFAULT STREAMLIT ELEMENTS */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* CARD STYLING */
        .css-1r6slb0, .stMarkdown, .stButton {
            text-align: center;
        }
        
        /* INPUT FIELDS */
        .stTextInput>div>div>input {
            background-color: rgba(255, 255, 255, 0.1);
            color: #fff;
            border: 1px solid #4e4eae;
            border-radius: 10px;
            text-align: center;
        }

        /* BUTTONS */
        .stButton>button {
            background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 16px;
            box-shadow: 0 4px 15px rgba(0, 210, 255, 0.4);
            width: 100%;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0 6px 20px rgba(0, 210, 255, 0.6);
        }

        /* METRIC CARDS */
        div[data-testid="stMetricValue"] {
            font-size: 24px;
            color: #00d2ff;
        }
    </style>
    """, unsafe_allow_html=True)

# --- MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Neuro-Viral", page_icon="🧬", layout="centered")
    apply_style()
    init_db()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- HEADER ---
    st.markdown(f"<h1 style='text-align: center; color: #00d2ff;'>{APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; opacity: 0.7;'>{VERSION}</p>", unsafe_allow_html=True)

    # --- LOGIN SCREEN ---
    if not st.session_state.logged_in:
        st.markdown("### 🔐 ACCESS CONTROL")
        
        # Admin Bypass Tab
        tab1, tab2 = st.tabs(["User Login", "Admin Gen"])
        
        with tab1:
            username = st.text_input("Username", placeholder="Enter ID")
            key = st.text_input("License Key", type="password", placeholder="EMP-XXXX-XXXX")
            
            if st.button("INITIATE UPLINK"):
                if username and key:
                    with st.spinner("Connecting to Neural Net..."):
                        time.sleep(1.5)
                        success, msg = check_license_in_db(username, key)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user = username
                            st.toast(msg, icon="✅")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(msg)
        
        with tab2:
            st.warning("Admin Access Only")
            adm_pass = st.text_input("Admin Key", type="password")
            target_user = st.text_input("Generate for User:")
            if st.button("Generate Key"):
                if adm_pass == "admin2026": # Simple admin pass
                    new_key = generate_license_hash(target_user)
                    st.code(new_key)
                else:
                    st.error("Access Denied")

    # --- DASHBOARD SCREEN ---
    else:
        st.success(f"Connection Secure: {st.session_state.user.upper()}")
        
        # Fake "Real-time" Analysis Graph
        st.markdown("### 📡 ALGORITHM PULSE")
        chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["TikTok", "Insta", "YouTube"])
        st.line_chart(chart_data)
        
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Viral Potential", value="High", delta="+12%")
        with col2:
            st.metric(label="Server Load", value="Stable", delta_color="off")

        st.markdown("### 🧬 GENERATE STRATEGY")
        if st.button("ANALYZE & DEPLOY"):
            # Simulation of processing
            progress_text = "Scanning Social Graph..."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text="Decripting Trends...")
            
            # Select Strategy
            daily_seed = st.session_state.user + time.strftime("%Y%m%d")
            random.seed(daily_seed)
            selected = random.choice(STRATEGIES)
            
            st.balloons()
            
            # Result Card
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border-left: 5px solid #00d2ff;">
                <h3 style="color: #00d2ff;">{selected['title']}</h3>
                <p style="font-size: 18px;">{selected['desc']}</p>
                <hr style="border-color: rgba(255,255,255,0.1);">
                <small>Viral Probability Score: {selected['score']}%</small>
            </div>
            """, unsafe_allow_html=True)
            
        if st.button("LOGOUT", type="secondary"):
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    main()
