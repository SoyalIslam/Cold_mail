import streamlit as st
import os
from dotenv import load_dotenv
from app.core.database import init_db, seed_templates, verify_user, create_user
from app.ui_st.send_page import send_page
from app.ui_st.templates_page import templates_page
from app.ui_st.settings_page import settings_page
from app.ui_st.tracking_page import tracking_page

# Load environment variables
load_dotenv()

# Set Streamlit page config
st.set_page_config(page_title="BeCold - Recruitment Outreach", page_icon="🚀", layout="wide")

def login_signup_page():
    st.title("🚀 BeCold - Recruitment Outreach")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        login_user = st.text_input("Username", key="login_username")
        login_pass = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            user = verify_user(login_user, login_pass)
            if user:
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = user['id']
                st.session_state["username"] = user['username']
                seed_templates(user['id']) # Seed default templates for new users
                st.success(f"Welcome back, {login_user}!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        st.subheader("Create New Account")
        new_user = st.text_input("Username", key="signup_username")
        new_pass = st.text_input("Password", type="password", key="signup_password")
        confirm_pass = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        if st.button("Sign Up"):
            if new_pass != confirm_pass:
                st.error("Passwords do not match")
            elif len(new_pass) < 6:
                st.error("Password must be at least 6 characters")
            else:
                success, msg = create_user(new_user, new_pass)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

def main():
    # Initialize the database
    init_db()

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        login_signup_page()
        st.stop()

    # Sidebar Navigation
    st.sidebar.title(f"🚀 BeCold ({st.session_state['username']})")
    
    page = st.sidebar.radio("Go to", ["Send Email", "Tracking", "Templates", "Settings"])

    if page == "Send Email":
        send_page()
    elif page == "Tracking":
        tracking_page()
    elif page == "Templates":
        templates_page()
    elif page == "Settings":
        settings_page()

    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
        st.rerun()

if __name__ == "__main__":
    main()
