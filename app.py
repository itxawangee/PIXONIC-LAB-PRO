import os
import tkinter as tk
from tkinter import ttk
import json
import hashlib
import uuid
from datetime import datetime
from project_manager import ProjectManager

class ProfessionalMediaEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PIXONIC LAB PRO")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Theme management
        self.current_theme = "dark"
        self.themes = {
            "dark": {
                "primary": "#2E3440",
                "secondary": "#3B4252",
                "background": "#121212",
                "text": "#E5E9F0",
                "accent1": "#5E81AC",
                "accent2": "#81A1C1",
                "accent3": "#88C0D0",
                "button": "#4C566A",
                "highlight": "#8FBCBB",
                "card": "#1E1E1E"
            },
            "light": {
                "primary": "#FFFFFF",
                "secondary": "#F5F5F5",
                "background": "#FAFAFA",
                "text": "#333333",
                "accent1": "#FF6B6B",
                "accent2": "#4ECDC4",
                "accent3": "#FFE66D",
                "button": "#E0E0E0",
                "highlight": "#A5D8FF",
                "card": "#FFFFFF"
            },
            "academic": {
                "primary": "#F8F9FA",
                "secondary": "#E9ECEF",
                "background": "#FFFFFF",
                "text": "#212529",
                "accent1": "#1A759F",
                "accent2": "#184E77",
                "accent3": "#34A0A4",
                "button": "#DEE2E6",
                "highlight": "#FFD166",
                "card": "#F8F9FA"
            },
            "Russian": {
                "primary": "#FFF0F6",
                "secondary": "#FDE2FF",
                "background": "#FFFFFF",
                "text": "#4A154B",
                "accent1": "#FF69B4",
                "accent2": "#C71585",
                "accent3": "#FFB6C1",
                "button": "#F8C8DC",
                "highlight": "#FFD1DC",
                "card": "#FFF5FA"
            },
            "windows7": {
                "primary": "#E3F2FD",
                "secondary": "#BBDEFB",
                "background": "#FFFFFF",
                "text": "#0D1A26",
                "accent1": "#1E88E5",
                "accent2": "#1565C0",
                "accent3": "#64B5F6",
                "button": "#E0E0E0",
                "highlight": "#B3E5FC",
                "card": "#F5F5F5"
            }
        }
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Database setup
        self.db_file = "users_db.json"
        self.current_user = None
        self.session_id = None
        self.project_manager = ProjectManager(self)
        
        # AI Services Configuration
        self.ai_services = {
            "image_enhancement": {
                "url": "https://platform.openai.com/image-enhancement",
                "key": "YOUR_API_KEY"
            },
            "object_removal": {
                "url": "https://platform.openai.com/object-removal",
                "key": "YOUR_API_KEY"
            },
            "style_transfer": {
                "url": "https://platform.openai.com/style-transfer",
                "key": "YOUR_API_KEYe"
            },
            "audio_enhancement": {
                "url": "https://platform.openai.com/audio-enhancement",
                "key": "YOUR_API_KEY"
            },
            "noise_reduction": {
                "url": "https://platform.openai.com/noise-reduction",
                "key": "YOUR_API_KEY"
            }
        }
        
        # Create containers
        self.container = ttk.Frame(self.root)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Initialize all frames
        self.frames = {}
        from pages.splash_screen import SplashScreen
        from pages.login_page import LoginPage
        from pages.signup_page import SignupPage
        from pages.dashboard_page import DashboardPage
        from pages.media_editor_page import MediaEditorPage
        from pages.profile_page import ProfilePage
        from pages.help_page import HelpPage
        
        for F in (SplashScreen, LoginPage, SignupPage, DashboardPage, 
                 MediaEditorPage, ProfilePage, HelpPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show splash screen first
        self.show_frame("SplashScreen")
        
        # Cleanup on exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def configure_styles(self):
        """Configure custom styles for the application"""
        theme = self.themes[self.current_theme]
        
        # Font configurations
        self.header_font = ("Helvetica", 18, "bold")
        self.body_font = ("Helvetica", 14)
        
        # Main style configuration
        self.style.configure('.', 
                           background=theme['background'],
                           foreground=theme['text'],
                           font=self.body_font)
        
        # Frame styles
        self.style.configure('TFrame', background=theme['background'])
        self.style.configure('Card.TFrame', 
                           background=theme['card'],
                           borderwidth=2,
                           relief='groove')
        self.style.configure('Toolbar.TFrame',
                           background=theme['secondary'],
                           relief='raised')
        
        # Label styles
        self.style.configure('Title.TLabel', 
                           font=("Helvetica", 24, "bold"),
                           background=theme['background'],
                           foreground=theme['accent1'])
        self.style.configure('Header.TLabel', 
                           font=("Helvetica", 16, "bold"),
                           background=theme['background'],
                           foreground=theme['accent2'])
        self.style.configure('Subheader.TLabel', 
                           font=("Helvetica", 12),
                           background=theme['background'],
                           foreground=theme['text'])
        
        # Button styles
        self.style.configure('TButton', 
                           font=self.body_font,
                           padding=6,
                           background=theme['button'])
        self.style.configure('Primary.TButton', 
                           foreground='white',
                           background=theme['accent1'])
        self.style.map('Primary.TButton',
                      background=[('active', theme['highlight']), 
                                 ('pressed', theme['accent3'])])
        self.style.configure('Secondary.TButton',
                           foreground=theme['text'],
                           background=theme['secondary'])
        self.style.configure('Success.TButton',
                           foreground='white',
                           background='#28a745')
        self.style.configure('Danger.TButton',
                           foreground='white',
                           background='#dc3545')
        self.style.configure('Info.TButton',
                           foreground='white',
                           background='#17a2b8')
        self.style.configure('Tool.TButton',
                           foreground=theme['text'],
                           background=theme['secondary'],
                           padding=3)
        
        # Notebook styles
        self.style.configure('TNotebook', background=theme['secondary'])
        self.style.configure('TNotebook.Tab', 
                           font=("Helvetica", 10, "bold"),
                           padding=6,
                           background=theme['secondary'],
                           foreground=theme['text'])
        
        # Entry styles
        self.style.configure('TEntry',
                           fieldbackground=theme['card'],
                           foreground=theme['text'])
        
        # Combobox styles
        self.style.configure('TCombobox',
                           fieldbackground=theme['card'],
                           foreground=theme['text'])
        
    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()
        
    def login_user(self, username, password):
        """Authenticate user"""
        try:
            with open(self.db_file, 'r') as f:
                users = json.load(f)
                
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            
            if username in users and users[username]['password'] == hashed_pw:
                self.current_user = username
                self.session_id = str(uuid.uuid4())
                self.project_manager.new_project()
                self.show_frame("DashboardPage")
                return True
            return False
        except (FileNotFoundError, json.JSONDecodeError):
            return False
            
    def create_user(self, username, password, email):
        """Create new user account"""
        try:
            # Try to load existing users
            try:
                with open(self.db_file, 'r') as f:
                    users = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                users = {}
                
            if username in users:
                return False  # Username exists
                
            # Hash password
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            
            # Create user record
            users[username] = {
                'password': hashed_pw,
                'email': email,
                'created_at': str(datetime.now()),
                'preferences': {
                    'image_format': 'png',
                    'audio_format': 'mp3',
                    'theme': 'dark'
                }
            }
            
            # Save to file
            with open(self.db_file, 'w') as f:
                json.dump(users, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
            
    def on_closing(self):
        """Cleanup before closing"""
        self.root.destroy()