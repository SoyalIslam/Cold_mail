import customtkinter as ctk
from app.ui.tabs.send_tab import SendTab
from app.ui.tabs.templates_tab import TemplatesTab
from app.ui.tabs.settings_tab import SettingsTab

class BeColdApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("BeCold - Student Recruitment Outreach")
        self.root.geometry("1000x700")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configure grid layout
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.sidebar_frame = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BeCold", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.send_button = ctk.CTkButton(self.sidebar_frame, text="Send Email", command=self.show_send_tab)
        self.send_button.grid(row=1, column=0, padx=20, pady=10)

        self.templates_button = ctk.CTkButton(self.sidebar_frame, text="Templates", command=self.show_templates_tab)
        self.templates_button.grid(row=2, column=0, padx=20, pady=10)

        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="Settings", command=self.show_settings_tab)
        self.settings_button.grid(row=3, column=0, padx=20, pady=10)

        # Main content area
        self.content_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Initialize tabs
        self.tabs = {
            "send": SendTab(self.content_frame),
            "templates": TemplatesTab(self.content_frame),
            "settings": SettingsTab(self.content_frame)
        }

        # Show default tab
        self.show_send_tab()

    def show_send_tab(self):
        self.show_tab("send")

    def show_templates_tab(self):
        self.show_tab("templates")

    def show_settings_tab(self):
        self.show_tab("settings")

    def show_tab(self, tab_name):
        for name, tab in self.tabs.items():
            if name == tab_name:
                tab.grid(row=0, column=0, sticky="nsew")
            else:
                tab.grid_forget()

    def run(self):
        self.root.mainloop()
