import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
from app.core.database import get_all_templates
from app.core.scheduler import schedule_email_task
from app.core.file_handler import process_and_send_batch

class SendTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="Send Cold Emails", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=20)

        # File selection
        self.csv_path = None
        self.resume_path = None

        self.csv_button = ctk.CTkButton(self, text="Select Recipient CSV", command=self.select_csv)
        self.csv_button.pack(pady=10)
        self.csv_label = ctk.CTkLabel(self, text="No CSV selected", wraplength=400)
        self.csv_label.pack()

        self.resume_button = ctk.CTkButton(self, text="Select Resume/CV", command=self.select_resume)
        self.resume_button.pack(pady=10)
        self.resume_label = ctk.CTkLabel(self, text="No Resume selected", wraplength=400)
        self.resume_label.pack()

        # Template Selection
        self.template_label = ctk.CTkLabel(self, text="Select Template")
        self.template_label.pack(pady=(20, 0))
        
        self.template_option = ctk.CTkOptionMenu(self, values=["Default"])
        self.template_option.pack(pady=10)

        # Scheduling
        self.date_label = ctk.CTkLabel(self, text="Schedule Date (YYYY-MM-DD)")
        self.date_label.pack(pady=(10, 0))
        self.date_entry = ctk.CTkEntry(self, placeholder_text=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(pady=5)

        self.time_label = ctk.CTkLabel(self, text="Schedule Time (HH:MM)")
        self.time_label.pack(pady=(10, 0))
        self.time_entry = ctk.CTkEntry(self, placeholder_text=datetime.now().strftime("%H:%M"))
        self.time_entry.pack(pady=5)

        self.send_button = ctk.CTkButton(self, text="Schedule/Send", fg_color="green", command=self.handle_send)
        self.send_button.pack(pady=30)

        self.update_templates()

    def select_csv(self):
        self.csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.csv_path:
            self.csv_label.configure(text=self.csv_path)

    def select_resume(self):
        self.resume_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx")])
        if self.resume_path:
            self.resume_label.configure(text=self.resume_path)

    def update_templates(self):
        templates = get_all_templates()
        names = [t['name'] for t in templates]
        if names:
            self.template_option.configure(values=names)
        else:
            self.template_option.configure(values=["No templates found"])

    def handle_send(self):
        if not self.csv_path or not self.resume_path:
            messagebox.showerror("Error", "Please select both a CSV file and a Resume.")
            return

        template_name = self.template_option.get()
        date_str = self.date_entry.get() or datetime.now().strftime("%Y-%m-%d")
        time_str = self.time_entry.get() or datetime.now().strftime("%H:%M")

        try:
            scheduled_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid date or time format. Please use YYYY-MM-DD and HH:MM.")
            return

        # Check if scheduled time is in the future
        if scheduled_time < datetime.now():
            # If time has passed, ask if they want to send now
            if messagebox.askyesno("Time Passed", "The scheduled time is in the past. Send now?"):
                scheduled_time = datetime.now()
            else:
                return

        # Schedule the task
        schedule_email_task(
            scheduled_time,
            process_and_send_batch,
            self.csv_path,
            self.resume_path,
            template_name
        )

        messagebox.showinfo("Success", f"Task scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
