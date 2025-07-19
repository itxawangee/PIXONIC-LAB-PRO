import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.configure(style='TFrame')
        self.create_widgets()
        
    def create_widgets(self):
        """Create login form widgets"""
        # Main container
        main_container = ttk.Frame(self, style='TFrame')
        main_container.pack(expand=True, fill=tk.BOTH, padx=100, pady=50)
        
        # Left panel - branding
        left_panel = ttk.Frame(main_container, style='TFrame')
        left_panel.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        logo = ttk.Label(left_panel, text="PIXONIC LAB PRO", 
                        style='Title.TLabel')
        logo.pack(pady=50)
        
        tagline = ttk.Label(left_panel, 
                           text="One studio. Endless creativity", 
                           style='Header.TLabel', justify=tk.CENTER)
        tagline.pack(pady=20)
        
        # Right panel - login form
        right_panel = ttk.Frame(main_container, style='TFrame')
        right_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        # Form container
        form_container = ttk.Frame(right_panel, style='TFrame')
        form_container.pack(expand=True, fill=tk.BOTH)
        
        # Header
        ttk.Label(form_container, text="Login", style='Title.TLabel').pack(pady=20)
        
        # Form fields
        ttk.Label(form_container, text="Username", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.username_entry = ttk.Entry(form_container, style='TEntry')
        self.username_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(form_container, text="Password", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.password_entry = ttk.Entry(form_container, show="*", style='TEntry')
        self.password_entry.pack(fill=tk.X, pady=5)
        
        # Remember me checkbox
        self.remember_var = tk.IntVar()
        ttk.Checkbutton(form_container, text="Remember me", variable=self.remember_var).pack(anchor=tk.W, pady=5)
        
        # Login button
        ttk.Button(form_container, text="Login", style='Primary.TButton',
                  command=self.login).pack(fill=tk.X, pady=20)
        
        # Sign up link
        signup_frame = ttk.Frame(form_container, style='TFrame')
        signup_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(signup_frame, text="Don't have an account?", style='Subheader.TLabel').pack(side=tk.LEFT)
        signup_btn = ttk.Button(signup_frame, text="Sign up", 
                              command=lambda: self.controller.show_frame("SignupPage"),
                              style='TButton')
        signup_btn.pack(side=tk.LEFT, padx=5)
        
        # Forgot password link
        ttk.Button(form_container, text="Forgot password?", 
                 command=self.forgot_password, style='TButton').pack(anchor=tk.E)
        
        # Status label
        self.status_label = ttk.Label(form_container, text="", foreground="red")
        self.status_label.pack(pady=10)
        
        # Footer
        footer = ttk.Frame(self, style='TFrame')
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        ttk.Label(footer, text="© 2023 PIXONIC LAB PRO. All rights reserved.", 
                 style='Subheader.TLabel').pack()
        
    def login(self):
        """Handle login attempt"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_label.config(text="Please enter both username and password")
            return
            
        if self.controller.login_user(username, password):
            self.status_label.config(text="")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            self.status_label.config(text="Invalid username or password")
    
    def forgot_password(self):
        """Handle forgot password"""
        messagebox.showinfo("Forgot Password", 
                          "Please contact support@promediaeditor.com to reset your password.")
        