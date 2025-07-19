import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

class SignupPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.configure(style='TFrame')
        self.create_widgets()
        
    def create_widgets(self):
        """Create signup form widgets"""
        # Main container
        main_container = ttk.Frame(self, style='TFrame')
        main_container.pack(expand=True, fill=tk.BOTH, padx=100, pady=50)
        
        # Form container
        form_container = ttk.Frame(main_container, style='TFrame')
        form_container.pack(expand=True, fill=tk.BOTH)
        
        # Header
        ttk.Label(form_container, text="Create Account", style='Title.TLabel').pack(pady=20)
        
        # Form fields
        ttk.Label(form_container, text="Username", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.username_entry = ttk.Entry(form_container, style='TEntry')
        self.username_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(form_container, text="Email", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.email_entry = ttk.Entry(form_container, style='TEntry')
        self.email_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(form_container, text="Password", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.password_entry = ttk.Entry(form_container, show="*", style='TEntry')
        self.password_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(form_container, text="Confirm Password", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.confirm_entry = ttk.Entry(form_container, show="*", style='TEntry')
        self.confirm_entry.pack(fill=tk.X, pady=5)
        
        # Terms checkbox
        self.terms_var = tk.IntVar()
        terms_frame = ttk.Frame(form_container, style='TFrame')
        terms_frame.pack(fill=tk.X, pady=10)
        
        ttk.Checkbutton(terms_frame, variable=self.terms_var).pack(side=tk.LEFT)
        ttk.Label(terms_frame, text="I agree to the").pack(side=tk.LEFT, padx=5)
        ttk.Button(terms_frame, text="Terms of Service", 
                  command=self.show_terms, style='TButton').pack(side=tk.LEFT)
        
        # Sign up button
        ttk.Button(form_container, text="Sign Up", style='Success.TButton',
                  command=self.signup).pack(fill=tk.X, pady=20)
        
        # Login link
        login_frame = ttk.Frame(form_container, style='TFrame')
        login_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(login_frame, text="Already have an account?", style='Subheader.TLabel').pack(side=tk.LEFT)
        login_btn = ttk.Button(login_frame, text="Login", 
                             command=lambda: self.controller.show_frame("LoginPage"),
                             style='TButton')
        login_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(form_container, text="", foreground="red")
        self.status_label.pack(pady=10)
        
        # Footer
        footer = ttk.Frame(self, style='TFrame')
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        ttk.Label(footer, text="© 2023 PIXONIC LAB PRO. All rights reserved.", 
                 style='Subheader.TLabel').pack()
        
    def signup(self):
        """Handle signup attempt"""
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not username or not email or not password or not confirm:
            self.status_label.config(text="Please fill all fields")
            return
            
        if password != confirm:
            self.status_label.config(text="Passwords do not match")
            return
            
        if len(password) < 8:
            self.status_label.config(text="Password must be at least 8 characters")
            return
            
        if not self.terms_var.get():
            self.status_label.config(text="You must agree to the terms of service")
            return
            
        if self.controller.create_user(username, password, email):
            self.status_label.config(text="Account created successfully!", foreground="green")
            self.username_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.confirm_entry.delete(0, tk.END)
            
            # Auto-login after successful signup
            self.controller.login_user(username, password)
        else:
            self.status_label.config(text="Username already exists")
    
    def show_terms(self):
        """Open terms of service in web browser"""
        webbrowser.open("https://www.pixoniclabpro.com/terms-of-service")
        # This URL should point to the actual terms of service page