import streamlit as st
import pandas as pd
from app.core.database import get_all_jobs, get_job_details, delete_job, delete_specific_log
from app.core.scheduler import cancel_scheduled_job

def tracking_page():
    user_id = st.session_state['user_id']
    st.title("📊 Email Tracking Dashboard")
    st.write("Monitor your email batches and individual delivery statuses.")

    jobs = get_all_jobs(user_id)
    
    if not jobs:
        st.info("No email jobs scheduled or sent yet.")
        return

    for job in jobs:
        job_id = job['job_id']
        aps_id = job['aps_job_id']
        status = job['status']
        total = job['total_emails']
        sent = job['sent_emails']
        
        with st.expander(f"📦 Job: {job_id} | Template: {job['template_name']} | Status: {status}"):
            st.write(f"**Scheduled/Sent at:** {job['scheduled_time']}")
            
            # Progress Bar
            progress = sent / total if total > 0 else 0
            st.progress(progress, text=f"{sent}/{total} Emails Sent")

            # Actions Row
            col1, col2 = st.columns(2)
            with col1:
                if status == "Scheduled":
                    if st.button("Cancel Entire Batch", key=f"cancel_{job_id}"):
                        if aps_id:
                            cancel_scheduled_job(aps_id)
                        delete_job(job_id)
                        st.success(f"Job {job_id} canceled.")
                        st.rerun()
                else:
                    if st.button("Remove from View", key=f"del_job_{job_id}"):
                        delete_job(job_id)
                        st.success(f"Job {job_id} removed.")
                        st.rerun()

            # Logs Table
            st.subheader("Recipient Status")
            logs = get_job_details(job_id)
            if logs:
                for log in logs:
                    l_col1, l_col2, l_col3, l_col4 = st.columns([3, 3, 2, 2])
                    with l_col1:
                        st.write(f"**{log['recipient_name']}**")
                    with l_col2:
                        st.write(log['recipient_email'])
                    with l_col3:
                        st.write(f"`{log['status']}`")
                    with l_col4:
                        if status == "Scheduled" and log['status'] == "Scheduled":
                            if st.button("Remove", key=f"rem_log_{log['id']}"):
                                delete_specific_log(log['id'])
                                st.toast(f"Removed {log['recipient_email']}")
                                st.rerun()
            else:
                st.write("No recipients found for this job.")
