import pandas as pd
import sqlite3
from app.core.email_sender import send_cold_email
from app.core.database import get_user_by_id, get_all_templates, update_job_status, get_db_connection

def process_and_send_batch(user_id, job_id, csv_path, resume_path, template_name):
    """
    Reads recipients from DB and sends emails using user-specific settings.
    """
    update_job_status(job_id, "Processing")
    
    user = get_user_by_id(user_id)
    if not user:
        update_job_status(job_id, "Failed: User not found")
        return
    
    templates = get_all_templates(user_id)
    template = next((t for t in templates if t['name'] == template_name), None)
    
    if not template:
        update_job_status(job_id, f"Failed: Template '{template_name}' not found")
        return

    template_content = template['content']
    template_subject = template['subject'] if template['subject'] else f"Application for {{Role}} - {{SENDER_NAME}}"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, recipient_email, recipient_name, role, company FROM job_logs WHERE job_id=? AND status='Scheduled'", (job_id,))
    recipients = cursor.fetchall()
    
    if not recipients:
        update_job_status(job_id, "Completed (No recipients)")
        conn.close()
        return

    for r in recipients:
        log_db_id = r['id']
        email = r['recipient_email']
        name = r['recipient_name']
        role = r['role'] if r['role'] else "Position"
        company = r['company'] if r['company'] else "your company"

        try:
            final_subject = template_subject.format(Company=company, Role=role, SENDER_NAME=user['full_name'] or user['username'])
            final_content = template_content.format(Name=name, Company=company, Role=role, SENDER_NAME=user['full_name'] or user['username'])
            
            success, msg = send_cold_email(user_id, email, final_subject, final_content, resume_path)
            if success:
                cursor.execute("UPDATE job_logs SET status='Sent' WHERE id=?", (log_db_id,))
                update_job_status(job_id, "Processing", sent_increment=1)
            else:
                cursor.execute("UPDATE job_logs SET status=? WHERE id=?", (f"Failed: {msg}", log_db_id))
        except Exception as e:
            cursor.execute("UPDATE job_logs SET status=? WHERE id=?", (f"Error: {str(e)}", log_db_id))
        
        conn.commit()
            
    update_job_status(job_id, "Completed")
    conn.close()
