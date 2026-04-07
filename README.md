# 🚀 BeCold: Automated Student Recruitment Outreach

**BeCold** is a powerful, Python-based automation tool designed to help students streamline their job search by automating cold emails to HR managers and company employees. It features a modern Streamlit interface, AI-powered template generation, and a precise scheduling system.

---

## ✨ Key Features

- **👥 Multi-User System**: Secure Login/Sign-up with encrypted password storage (`bcrypt`).
- **📅 Interactive Clock Scheduler**: A visual analog + digital scheduler using Plotly dials and sliders for precise timing.
- **🤖 AI Template Generator**: Integrated with OpenAI to generate professional cold emails based on simple prompts.
- **📄 Template Manager**: 
  - Save, Edit, and Delete custom templates.
  - Pre-seeded professional templates for AI/ML, Full Stack, DevOps, and Cybersecurity roles.
- **📊 Real-Time Tracking**: 
  - Monitor batch progress (Scheduled, Processing, Completed).
  - Individual email logs with status (Sent, Failed, Error).
  - Selective removal: Delete specific recipients from a scheduled batch before it sends.
- **📥 Flexible Input**: 
  - Upload a CSV list of recipients.
  - Manual Entry: Add/Edit recipients directly in the UI.
- **🔒 Security First**:
  - SMTP App Passwords are encrypted using Fernet symmetric encryption.
  - Private data isolation: Users can only see their own templates, jobs, and history.

---

## 🛠️ Tech Stack

- **UI**: [Streamlit](https://streamlit.io/)
- **Database**: SQLite (Local persistent storage)
- **Email**: [yagmail](https://github.com/kootenpv/yagmail) (SMTP)
- **Scheduling**: [APScheduler](https://apscheduler.readthedocs.io/)
- **AI**: [OpenAI API](https://openai.com/)
- **Visualization**: [Plotly](https://plotly.com/)
- **Security**: Cryptography (Fernet), Bcrypt

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/becold.git
cd becold
```

### 2. Install Dependencies
It is recommended to use a virtual environment.
```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a `.streamlit/secrets.toml` file in the root directory:
```toml
APP_PASSWORD = "your_admin_access_password"
```
*(Note: This password is for the initial access gate if you choose to keep it, though the app now uses a full multi-user login system.)*

### 4. Run the Application
```bash
streamlit run main.py
```

---

## 📖 How to Use

1.  **Sign Up**: Create a personal account.
2.  **Settings**: Go to the Settings tab and enter your:
    - Sender Name
    - Email Address
    - **SMTP App Password** (Critical for sending emails)
    - OpenAI API Key (Optional, for AI templates)
3.  **Templates**: Choose a pre-written template or generate a new one using the AI prompt. Add a custom subject line.
4.  **Send Email**:
    - Upload your `recipients.csv` or enter details manually.
    - Upload your **Resume/CV** (PDF/Docx).
    - Use the **Interactive Clock** to set the exact date and time.
5.  **Tracking**: Monitor your "Tracking" page to see your emails going out in real-time.

---

## 🌐 Deployment (Streamlit Cloud)

To deploy this privately and for free:
1.  Push your code to a **Private GitHub Repository**.
2.  Connect your repo to [Streamlit Community Cloud](https://share.streamlit.io/).
3.  In the Streamlit Cloud Dashboard, go to **Settings > Secrets** and paste the content of your `secrets.toml`.
4.  Invite specific people via email to grant them private access.

---

## ⚠️ Important Note: SMTP App Passwords
For Gmail users, you **must** use an "App Password" rather than your main account password. 
- Enable 2-Factor Authentication on your Google Account.
- Search for "App Passwords" in Google Security settings.
- Generate a password for "Mail" and "Other (Custom Name)".

---

## 📄 License
This project is licensed under the MIT License.
