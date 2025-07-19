import tkinter as tk
from tkinter import ttk, messagebox

class DashboardPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.configure(style='TFrame')
        self.create_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)
        
    def create_widgets(self):
        """Create dashboard widgets with separate panels"""
        # Header with theme switcher
        header_frame = ttk.Frame(self, style='TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.welcome_label = ttk.Label(header_frame, text="", style='Title.TLabel')
        self.welcome_label.pack(side=tk.LEFT)
        
        # Theme switcher
        theme_frame = ttk.Frame(header_frame)
        theme_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.controller.current_theme)
        theme_menu = ttk.OptionMenu(theme_frame, self.theme_var, 
                                   self.controller.current_theme,
                                   *self.controller.themes.keys(),
                                   command=self.change_theme)
        theme_menu.pack(side=tk.LEFT)
        
        # Main content with separate panels
        content_frame = ttk.Frame(self, style='TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Editor Panel
        editor_panel = ttk.LabelFrame(content_frame, text="Media Editor", 
                                    style='Card.TFrame', padding=15)
        editor_panel.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Editor content
        ttk.Label(editor_panel, 
                 text="Create. Combine. Control.\nA fusion of visuals and sound",
                 style='Header.TLabel',
                 justify=tk.CENTER).pack(pady=10)
        
        btn_frame = ttk.Frame(editor_panel)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Image Editor", style='Primary.TButton',
                  command=lambda: self.controller.show_frame("MediaEditorPage")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Audio Editor", style='Primary.TButton',
                  command=lambda: self.controller.show_frame("MediaEditorPage")).pack(side=tk.LEFT, padx=5)
        
        # Recent Projects Panel
        projects_panel = ttk.LabelFrame(content_frame, text="Recent Projects", 
                                      style='Card.TFrame', padding=15)
        projects_panel.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(projects_panel, text="No recent projects", 
                 style='Subheader.TLabel').pack(pady=20)
        
        # Footer with quick actions
        footer_frame = ttk.Frame(self, style='TFrame')
        footer_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(footer_frame, text="New Project", style='Success.TButton',
                  command=self.new_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(footer_frame, text="Help", style='Info.TButton',
                  command=lambda: self.controller.show_frame("HelpPage")).pack(side=tk.RIGHT, padx=5)
    
    def change_theme(self, theme_name):
        """Change application theme"""
        self.controller.current_theme = theme_name
        self.controller.configure_styles()
        # Force refresh of all widgets
        self.controller.show_frame("DashboardPage")
    
    def new_project(self):
        """Handle new project creation"""
        self.controller.project_manager.new_project()
        messagebox.showinfo("New Project", "Created new project successfully!")
    
    def on_show_frame(self, event):
        """Update welcome message when frame is shown"""
        self.welcome_label.config(text=f"Welcome, {self.controller.current_user}")
        # Update theme switcher to current theme
        self.theme_var.set(self.controller.current_theme)
                
    def logout(self):
        """Handle logout"""
        self.controller.current_user = None
        self.controller.session_id = None
        self.controller.show_frame("LoginPage")