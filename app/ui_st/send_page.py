import streamlit as st
import os
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import numpy as np
from app.core.database import get_all_templates, create_job_record, bulk_log_recipients
from app.core.scheduler import schedule_email_task
from app.core.file_handler import process_and_send_batch

def send_page():
    user_id = st.session_state['user_id']
    st.title("🚀 Send Cold Emails")

    input_method = st.radio("Choose input method:", ["Upload CSV", "Manual Entry"])
    df = pd.DataFrame(columns=["Name", "Email", "Company", "Role"])
    csv_file_name = "manual_entry.csv"

    if input_method == "Upload CSV":
        csv_file = st.file_uploader("Select Recipient CSV", type=["csv"])
        if csv_file:
            df = pd.read_csv(csv_file)
            csv_file_name = csv_file.name
    else:
        st.write("Enter recipient details below:")
        df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    if not df.empty:
        st.subheader("Recipient Preview")
        edited_df = st.data_editor(df, num_rows="dynamic", key="recipient_editor")
        st.info(f"Final recipient count: {len(edited_df)}")
        
        final_csv_path = os.path.join("uploads", f"final_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{csv_file_name}")
        if not os.path.exists("uploads"): os.makedirs("uploads")
        edited_df.to_csv(final_csv_path, index=False)
        st.session_state['current_csv'] = final_csv_path
        st.session_state['total_emails'] = len(edited_df)
        st.session_state['current_df'] = edited_df

    st.divider()

    resume_file = st.file_uploader("Select Resume/CV", type=["pdf", "docx"])
    if resume_file:
        resume_path = os.path.join("uploads", resume_file.name)
        with open(resume_path, "wb") as f:
            f.write(resume_file.getbuffer())
        st.session_state['current_resume'] = resume_path
        st.success(f"Resume '{resume_file.name}' uploaded.")

    st.divider()

    # Template selection
    templates = get_all_templates(user_id)
    template_names = [t['name'] for t in templates]
    selected_template = st.selectbox("Select Template", template_names) if template_names else st.warning("Create a template first.")

    # --- INTERACTIVE CLOCK SCHEDULER ---
    st.subheader("⏰ Interactive Clock Scheduler")
    
    if 'send_date' not in st.session_state:
        st.session_state['send_date'] = datetime.now().date()
    send_date = st.date_input("Select Date", value=st.session_state['send_date'])
    st.session_state['send_date'] = send_date

    if 'slider_hour' not in st.session_state:
        st.session_state['slider_hour'] = datetime.now().hour
    if 'slider_min' not in st.session_state:
        st.session_state['slider_min'] = datetime.now().minute

    c_q1, c_q2 = st.columns(2)
    if c_q1.button("Send Now"):
        st.session_state['slider_hour'] = datetime.now().hour
        st.session_state['slider_min'] = (datetime.now().minute + 1) % 60
        st.rerun()
    if c_q2.button("In 1 Hour"):
        st.session_state['slider_hour'] = (datetime.now().hour + 1) % 24
        st.rerun()

    # Visual Clock and Precise Sliders
    c_clock, c_sliders = st.columns([1, 1])
    
    with c_clock:
        st.plotly_chart(draw_clock_face(st.session_state['slider_hour'], st.session_state['slider_min']), use_container_width=False)
        st.write(f"### {st.session_state['slider_hour']:02d}:{st.session_state['slider_min']:02d}")

    with c_sliders:
        hour = st.slider("Hour", 0, 23, value=st.session_state['slider_hour'], key="h_slider_main")
        st.session_state['slider_hour'] = hour
        minute = st.slider("Minute", 0, 59, value=st.session_state['slider_min'], key="m_slider_main")
        st.session_state['slider_min'] = minute
        
        scheduled_datetime = datetime.combine(send_date, datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0).time())
        diff = scheduled_datetime - datetime.now()
        if diff.total_seconds() > 0:
            st.success(f"Sending in {int(diff.total_seconds() // 60)} minutes")
        else:
            st.warning("Sending Immediately")

    if st.button("Confirm & Schedule Emails", type="primary", use_container_width=True):
        if 'current_csv' not in st.session_state or 'current_resume' not in st.session_state:
            st.error("Missing Recipients or Resume.")
        elif not selected_template:
            st.error("No template selected.")
        else:
            job_id = f"job_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            aps_id = schedule_email_task(
                scheduled_datetime,
                process_and_send_batch,
                user_id,
                job_id,
                os.path.abspath(st.session_state['current_csv']),
                os.path.abspath(st.session_state['current_resume']),
                selected_template
            )
            
            create_job_record(user_id, job_id, aps_id, selected_template, scheduled_datetime, st.session_state['total_emails'])
            bulk_log_recipients(job_id, st.session_state['current_df'].to_dict('records'))
            
            st.success(f"Batch scheduled! Job ID: {job_id}")
            st.balloons()

def draw_clock_face(hour, minute):
    h_angle = (hour % 12 + minute / 60) * 30
    m_angle = minute * 6
    h_rad = np.radians(90 - h_angle)
    m_rad = np.radians(90 - m_angle)
    fig = go.Figure()
    fig.add_shape(type="circle", x0=-1.1, y0=-1.1, x1=1.1, y1=1.1, line_color="white", line_width=4)
    for i in range(1, 13):
        angle = np.radians(90 - i * 30)
        fig.add_annotation(x=np.cos(angle)*0.85, y=np.sin(angle)*0.85, text=str(i), showarrow=False, font=dict(size=16, color="white"))
    fig.add_shape(type="line", x0=0, y0=0, x1=np.cos(h_rad)*0.5, y1=np.sin(h_rad)*0.5, line=dict(color="red", width=6))
    fig.add_shape(type="line", x0=0, y0=0, x1=np.cos(m_rad)*0.75, y1=np.sin(m_rad)*0.75, line=dict(color="blue", width=4))
    fig.add_shape(type="circle", x0=-0.05, y0=-0.05, x1=0.05, y1=0.05, fillcolor="white", line_color="white")
    fig.update_layout(showlegend=False, width=300, height=300, margin=dict(l=0, r=0, t=0, b=0),
                      xaxis=dict(visible=False, range=[-1.2, 1.2]), yaxis=dict(visible=False, range=[-1.2, 1.2]),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig
