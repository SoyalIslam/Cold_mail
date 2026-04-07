import sqlite3
import os
import bcrypt

DB_PATH = "data/app.db"

def get_db_connection():
    if not os.path.exists("data"):
        os.makedirs("data")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Ensure Users table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            full_name TEXT,
            email TEXT,
            encrypted_smtp_password TEXT,
            openai_api_key TEXT
        )
    ''')
    
    # 2. Manual Migration for existing 'users' table
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    
    migrations = [
        ("username", "TEXT"),
        ("password_hash", "TEXT"),
        ("full_name", "TEXT"),
        ("encrypted_smtp_password", "TEXT"),
        ("openai_api_key", "TEXT"),
        ("name", "TEXT"), # Legacy compatibility
        ("email", "TEXT") # Legacy compatibility
    ]
    
    for col, col_type in migrations:
        if col not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass

    # 3. Templates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            subject TEXT,
            content TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute("PRAGMA table_info(templates)")
    if "user_id" not in [row[1] for row in cursor.fetchall()]:
        cursor.execute("ALTER TABLE templates ADD COLUMN user_id INTEGER")

    # 4. Jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            user_id INTEGER,
            aps_job_id TEXT,
            template_name TEXT,
            scheduled_time DATETIME,
            status TEXT DEFAULT 'Scheduled',
            total_emails INTEGER,
            sent_emails INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute("PRAGMA table_info(jobs)")
    existing_jobs_cols = [row[1] for row in cursor.fetchall()]
    if "user_id" not in existing_jobs_cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN user_id INTEGER")
    if "aps_job_id" not in existing_jobs_cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN aps_job_id TEXT")

    # 5. Job Logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            recipient_email TEXT,
            recipient_name TEXT,
            role TEXT,
            company TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        )
    ''')
    cursor.execute("PRAGMA table_info(job_logs)")
    if "company" not in [row[1] for row in cursor.fetchall()]:
        cursor.execute("ALTER TABLE job_logs ADD COLUMN company TEXT")

    conn.commit()
    conn.close()

# --- User Management ---
def create_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if username exists first to give clear feedback
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists."
        
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        # Provide defaults for all possible columns to satisfy legacy NOT NULL constraints
        cursor.execute('''
            INSERT INTO users (username, password_hash, full_name, name, email, encrypted_smtp_password, openai_api_key) 
            VALUES (?, ?, '', '', '', '', '')
        ''', (username, hashed))
        conn.commit()
        return True, "User created successfully"
    except sqlite3.Error as e:
        return False, f"Database Error: {str(e)}"
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and user['password_hash'] and bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return user
    return None

def update_user_settings(user_id, full_name, email, enc_smtp_pass, openai_key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET full_name=?, email=?, encrypted_smtp_password=?, openai_api_key=?, name=?, email=?
        WHERE id=?
    ''', (full_name, email, enc_smtp_pass, openai_key, full_name, email, user_id))
    conn.commit()
    conn.close()

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_template(user_id, name, subject, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM templates WHERE user_id=? AND name=?", (user_id, name))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE templates SET subject=?, content=? WHERE id=?", (subject, content, row['id']))
    else:
        cursor.execute("INSERT INTO templates (user_id, name, subject, content) VALUES (?, ?, ?, ?)", (user_id, name, subject, content))
    conn.commit()
    conn.close()

def get_all_templates(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM templates WHERE user_id=?", (user_id,))
    templates = cursor.fetchall()
    conn.close()
    return templates

def delete_template(user_id, template_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM templates WHERE id=? AND user_id=?", (template_id, user_id))
    conn.commit()
    conn.close()

def create_job_record(user_id, job_id, aps_job_id, template_name, scheduled_time, total_emails):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO jobs (job_id, user_id, aps_job_id, template_name, scheduled_time, total_emails, sent_emails)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    ''', (job_id, user_id, aps_job_id, template_name, scheduled_time, total_emails))
    conn.commit()
    conn.close()

def get_all_jobs(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE user_id=? ORDER BY scheduled_time DESC", (user_id,))
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def update_job_status(job_id, status, sent_increment=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET status=?, sent_emails = sent_emails + ? WHERE job_id=?", (status, sent_increment, job_id))
    conn.commit()
    conn.close()

def log_email_status(job_id, email, name, role, company, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO job_logs (job_id, recipient_email, recipient_name, role, company, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (job_id, email, name, role, company, status))
    conn.commit()
    conn.close()

def bulk_log_recipients(job_id, recipients_list):
    conn = get_db_connection()
    cursor = conn.cursor()
    logs = [(job_id, r.get('Email', ''), r.get('Name', ''), r.get('Role', ''), r.get('Company', ''), 'Scheduled') for r in recipients_list]
    cursor.executemany('''
        INSERT INTO job_logs (job_id, recipient_email, recipient_name, role, company, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', logs)
    conn.commit()
    conn.close()

def get_job_details(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_logs WHERE job_id=?", (job_id,))
    logs = cursor.fetchall()
    conn.close()
    return logs

def delete_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM job_logs WHERE job_id=?", (job_id,))
    cursor.execute("DELETE FROM jobs WHERE job_id=?", (job_id,))
    conn.commit()
    conn.close()

def delete_specific_log(log_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT job_id FROM job_logs WHERE id=?", (log_id,))
    job = cursor.fetchone()
    if job:
        cursor.execute("UPDATE jobs SET total_emails = total_emails - 1 WHERE job_id=?", (job['job_id'],))
        cursor.execute("DELETE FROM job_logs WHERE id=?", (log_id,))
    conn.commit()
    conn.close()

def seed_templates(user_id):
    templates = [
        ("AI/ML Engineer", "Inquiry: Machine Learning Opportunities at {Company}", "Dear {Name},\n\nI am reaching out to express my interest in AI/ML opportunities at {Company}. As a student specializing in Machine Learning, I have developed projects involving computer vision and NLP. I would love to bring my technical skills to your engineering team.\n\nBest regards,\n{SENDER_NAME}"),
        ("Full Stack Developer", "Application for {Role} - {SENDER_NAME}", "Dear {Name},\n\nI am writing to you regarding the {Role} opening at {Company}. I am a full-stack developer with experience in React and Node.js. I have a strong passion for building scalable web applications and would love to discuss how I can contribute to your team.\n\nBest regards,\n{SENDER_NAME}"),
        ("DevOps Engineer", "DevOps Engineering Interest - {SENDER_NAME}", "Dear {Name},\n\nI am highly interested in the DevOps culture at {Company}. My background includes working with Docker, Kubernetes, and CI/CD pipelines. I am eager to apply my automation skills to improve your deployment workflows as a {Role}.\n\nBest regards,\n{SENDER_NAME}"),
        ("Cybersecurity Analyst", "Securing {Company}'s Infrastructure - {SENDER_NAME}", "Dear {Name},\n\nSecurity is at the heart of every great product, which is why I am so interested in {Company}. As a student focused on cybersecurity, I have experience in penetration testing and network security. I would love the chance to help protect your infrastructure.\n\nBest regards,\n{SENDER_NAME}")
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM templates WHERE user_id=?", (user_id,))
    if cursor.fetchone()[0] == 0:
        logs = [(user_id, t[0], t[1], t[2]) for t in templates]
        cursor.executemany("INSERT INTO templates (user_id, name, subject, content) VALUES (?, ?, ?, ?)", logs)
        conn.commit()
    conn.close()
