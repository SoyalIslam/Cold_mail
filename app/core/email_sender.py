import yagmail
from app.core.database import get_user_by_id
from app.core.security import decrypt_password

def send_cold_email(user_id, recipient_email, subject, contents, attachment_path=None):
    user = get_user_by_id(user_id)
    if not user or not user['encrypted_smtp_password']:
        return False, "SMTP settings not configured for this user."
    
    try:
        # Decrypt password for SMTP
        password = decrypt_password(user['encrypted_smtp_password'])
        
        # Initialize yagmail client
        yag = yagmail.SMTP(user['email'], password)
        
        # Send email
        yag.send(
            to=recipient_email,
            subject=subject,
            contents=contents,
            attachments=attachment_path
        )
        return True, "Email sent successfully."
    except Exception as e:
        return False, f"SMTP Error: {str(e)}"
