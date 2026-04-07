import customtkinter as ctk
from app.core.database import save_template, get_all_templates
from app.core.ai_handler import generate_ai_template

class TemplatesTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="Template Manager", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=20)

        # AI Prompt
        self.ai_prompt_label = ctk.CTkLabel(self, text="AI Prompt (e.g., 'A cold email for a Software Engineer role')")
        self.ai_prompt_label.pack(pady=(10, 0))
        self.ai_prompt_entry = ctk.CTkEntry(self, width=600)
        self.ai_prompt_entry.pack(pady=(0, 10))
        
        self.ai_gen_button = ctk.CTkButton(self, text="Generate with AI", command=self.generate_with_ai)
        self.ai_gen_button.pack(pady=10)

        # Template Editor
        self.name_label = ctk.CTkLabel(self, text="Template Name")
        self.name_label.pack(pady=(20, 0))
        self.name_entry = ctk.CTkEntry(self, width=600)
        self.name_entry.pack(pady=(0, 10))

        self.content_label = ctk.CTkLabel(self, text="Email Content (Use {Name}, {Company}, {Role}, {SENDER_NAME})")
        self.content_label.pack(pady=(10, 0))
        self.content_text = ctk.CTkTextbox(self, width=600, height=300)
        self.content_text.pack(pady=(0, 20))

        self.save_button = ctk.CTkButton(self, text="Save Template", command=self.save_template)
        self.save_button.pack(pady=10)

    def generate_with_ai(self):
        prompt = self.ai_prompt_entry.get()
        if prompt:
            self.ai_gen_button.configure(state="disabled", text="Generating...")
            # We would ideally run this in a thread to keep UI responsive
            response = generate_ai_template(prompt)
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", response)
            self.ai_gen_button.configure(state="normal", text="Generate with AI")

    def save_template(self):
        name = self.name_entry.get()
        content = self.content_text.get("1.0", "end-1c")
        if name and content:
            save_template(name, content)
            print(f"Template '{name}' saved.")
