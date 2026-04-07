import streamlit as st
from app.core.database import save_template, get_all_templates, delete_template
from app.core.ai_handler import generate_ai_template

def templates_page():
    user_id = st.session_state['user_id']
    st.title("📄 Template Manager")

    if 'edit_template_content' not in st.session_state:
        st.session_state['edit_template_content'] = ""
    if 'edit_template_name' not in st.session_state:
        st.session_state['edit_template_name'] = ""
    if 'edit_template_subject' not in st.session_state:
        st.session_state['edit_template_subject'] = ""

    st.subheader("🤖 Generate with AI")
    ai_prompt = st.text_input("Describe the email template you need")
    if st.button("Generate with AI"):
        if ai_prompt:
            with st.spinner("AI is thinking..."):
                response = generate_ai_template(ai_prompt)
                st.session_state['edit_template_content'] = response
                st.rerun()
        else:
            st.warning("Please enter a prompt.")

    st.divider()

    st.subheader("✏️ Create / Edit Template")
    with st.form("template_form", clear_on_submit=True):
        name = st.text_input("Template Name", value=st.session_state['edit_template_name'])
        subject = st.text_input("Email Subject", value=st.session_state['edit_template_subject'])
        content = st.text_area("Email Content", height=300, value=st.session_state['edit_template_content'])
        
        submitted = st.form_submit_button("Save Template")
        if submitted:
            if name and content:
                save_template(user_id, name, subject, content)
                st.success(f"Template '{name}' saved.")
                st.session_state['edit_template_content'] = ""
                st.session_state['edit_template_name'] = ""
                st.session_state['edit_template_subject'] = ""
                st.rerun()
            else:
                st.error("Name and Content are required.")

    st.divider()
    st.subheader("📚 Your Templates")
    templates = get_all_templates(user_id)
    if templates:
        for t in templates:
            col1, col2, col3 = st.columns([6, 1, 1])
            with col1:
                with st.expander(f"📌 {t['name']}"):
                    st.write(f"**Subject:** {t['subject']}")
                    st.code(t['content'])
            with col2:
                if st.button("Edit", key=f"edit_{t['id']}"):
                    st.session_state['edit_template_content'] = t['content']
                    st.session_state['edit_template_name'] = t['name']
                    st.session_state['edit_template_subject'] = t['subject'] if t['subject'] else ""
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"del_{t['id']}"):
                    delete_template(user_id, t['id'])
                    st.rerun()
    else:
        st.write("No templates saved yet.")
