import customtkinter as ctk
from app.core.database import save_user, get_user
from app.core.security import encrypt_password, decrypt_password

class SettingsTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        
        self.label = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=20)

        # User Info
        self.name_entry = self.create_input("User Name")
        self.email_entry = self.create_input("Your Email (Gmail/Outlook)")
        self.pass_entry = self.create_input("App Password", show="*")
        self.openai_entry = self.create_input("OpenAI API Key", show="*")

        self.save_button = ctk.CTkButton(self, text="Save Settings", command=self.save_settings)
        self.save_button.pack(pady=20)

        self.load_settings()

    def create_input(self, label_text, show=None):
        label = ctk.CTkLabel(self, text=label_text)
        label.pack(pady=(10, 0))
        entry = ctk.CTkEntry(self, width=400, show=show)
        entry.pack(pady=(0, 10))
        return entry

    def save_settings(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.pass_entry.get()
        openai_key = self.openai_entry.get()

        encrypted_pass = encrypt_password(password) if password else ""
        save_user(name, email, encrypted_pass, openai_key)
        print("Settings saved successfully!")

    def load_settings(self):
        user = get_user()
        if user:
            self.name_entry.insert(0, user['name'])
            self.email_entry.insert(0, user['email'])
            if user['openai_api_key']:
                self.openai_entry.insert(0, user['openai_api_key'])
            # We don't decrypt password back to UI for security, but we could if needed
            # decrypted_pass = decrypt_password(user['encrypted_password'])
            # self.pass_entry.insert(0, decrypted_pass)
