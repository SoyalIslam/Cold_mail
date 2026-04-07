import streamlit as st
from app.core.database import update_user_settings, get_user_by_id
from app.core.security import encrypt_password

def settings_page():
    st.title("⚙️ User Settings")
    st.write("Configure your profile and email credentials.")

    user_id = st.session_state['user_id']
    user = get_user_by_id(user_id)
    
    with st.form("settings_form"):
        full_name = st.text_input("Full Name (Sender Name)", value=user['full_name'] if user['full_name'] else "")
        email = st.text_input("Your Email (Gmail/Outlook)", value=user['email'] if user['email'] else "")
        smtp_password = st.text_input("SMTP App Password", type="password", help="Use an App Password for safety.")
        openai_key = st.text_input("OpenAI API Key", type="password", value=user['openai_api_key'] if user['openai_api_key'] else "")
        
        submitted = st.form_submit_button("Update Settings")
        if submitted:
            if not email:
                st.error("Email is required for sending.")
            else:
                # Only re-encrypt if a new password was typed
                enc_pass = encrypt_password(smtp_password) if smtp_password else user['encrypted_smtp_password']
                update_user_settings(user_id, full_name, email, enc_pass, openai_key)
                st.success("Settings updated!")
                st.rerun()

    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
        st.rerun()
