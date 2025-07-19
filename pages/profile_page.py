import tkinter as tk
from tkinter import ttk, messagebox
import json
import hashlib

class ProfilePage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create profile page widgets"""
        # Header
        header_frame = ttk.Frame(self, style='TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(header_frame, text="User Profile", style='Title.TLabel').pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Back to Dashboard", style='Secondary.TButton',
                  command=lambda: self.controller.show_frame("DashboardPage")).pack(side=tk.RIGHT)
        
        # Main content
        content_frame = ttk.Frame(self, style='TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Profile info
        info_frame = ttk.LabelFrame(content_frame, text="Account Information", padding=15)
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text=f"Username: {self.controller.current_user}", 
                 style='Subheader.TLabel').pack(anchor=tk.W)
        
        # Load additional user data if available
        try:
            with open(self.controller.db_file, 'r') as f:
                users = json.load(f)
                user_data = users.get(self.controller.current_user, {})
                email = user_data.get('email', 'Not specified')
                created = user_data.get('created_at', 'Unknown')
                
                ttk.Label(info_frame, text=f"Email: {email}", 
                         style='Subheader.TLabel').pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Account created: {created}", 
                         style='Subheader.TLabel').pack(anchor=tk.W)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Preferences
        pref_frame = ttk.LabelFrame(content_frame, text="Preferences", padding=15)
        pref_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(pref_frame, text="Default Image Format:", 
                 style='Subheader.TLabel').pack(anchor=tk.W)
        self.img_format = ttk.Combobox(pref_frame, values=["PNG", "JPEG", "BMP"], 
                                      state="readonly")
        self.img_format.pack(fill=tk.X, pady=5)
        self.img_format.set("PNG")
        
        ttk.Label(pref_frame, text="Default Audio Format:", 
                 style='Subheader.TLabel').pack(anchor=tk.W)
        self.audio_format = ttk.Combobox(pref_frame, values=["WAV", "MP3", "FLAC"], 
                                        state="readonly")
        self.audio_format.pack(fill=tk.X, pady=5)
        self.audio_format.set("MP3")
        
        ttk.Button(pref_frame, text="Save Preferences", style='Primary.TButton',
                  command=self.save_preferences).pack(fill=tk.X, pady=5)
        
        # Account actions
        action_frame = ttk.LabelFrame(content_frame, text="Account Actions", padding=15)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Change Password", style='Primary.TButton',
                  command=self.change_password).pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="Delete Account", style='Danger.TButton',
                  command=self.delete_account).pack(fill=tk.X, pady=5)
    
    def save_preferences(self):
        """Save user preferences"""
        try:
            with open(self.controller.db_file, 'r') as f:
                users = json.load(f)
                
            if self.controller.current_user in users:
                users[self.controller.current_user]['preferences'] = {
                    'image_format': self.img_format.get().lower(),
                    'audio_format': self.audio_format.get().lower(),
                    'theme': self.controller.current_theme
                }
                
                with open(self.controller.db_file, 'w') as f:
                    json.dump(users, f, indent=2)
                
                messagebox.showinfo("Success", "Preferences saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save preferences: {e}")
    
    def change_password(self):
        """Change password dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("Change Password")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text="Change Password", style='Title.TLabel').pack(pady=10)
        
        ttk.Label(dialog, text="Current Password:", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 0))
        current_pw = ttk.Entry(dialog, show="*", style='TEntry')
        current_pw.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(dialog, text="New Password:", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 0))
        new_pw = ttk.Entry(dialog, show="*", style='TEntry')
        new_pw.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(dialog, text="Confirm New Password:", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 0))
        confirm_pw = ttk.Entry(dialog, show="*", style='TEntry')
        confirm_pw.pack(fill=tk.X, padx=20, pady=5)
        
        status = ttk.Label(dialog, text="", foreground="red")
        status.pack(pady=5)
        
        def update_password():
            current = current_pw.get()
            new = new_pw.get()
            confirm = confirm_pw.get()
            
            if not current or not new or not confirm:
                status.config(text="Please fill all fields")
                return
                
            if new != confirm:
                status.config(text="New passwords don't match")
                return
                
            if len(new) < 8:
                status.config(text="Password must be at least 8 characters")
                return
                
            try:
                with open(self.controller.db_file, 'r') as f:
                    users = json.load(f)
                    
                user = users.get(self.controller.current_user)
                if user:
                    hashed_current = hashlib.sha256(current.encode()).hexdigest()
                    if user['password'] == hashed_current:
                        hashed_new = hashlib.sha256(new.encode()).hexdigest()
                        user['password'] = hashed_new
                        
                        with open(self.controller.db_file, 'w') as f:
                            json.dump(users, f, indent=2)
                            
                        messagebox.showinfo("Success", "Password changed successfully")
                        dialog.destroy()
                    else:
                        status.config(text="Current password is incorrect")
            except Exception as e:
                messagebox.showerror("Error", f"Could not change password: {e}")
        
        ttk.Button(dialog, text="Update Password", style='Primary.TButton',
                  command=update_password).pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(dialog, text="Cancel", style='Secondary.TButton',
                  command=dialog.destroy).pack(fill=tk.X, padx=20, pady=5)
    
    def delete_account(self):
        """Delete account confirmation"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete your account? This cannot be undone."):
            try:
                with open(self.controller.db_file, 'r') as f:
                    users = json.load(f)
                
                if self.controller.current_user in users:
                    del users[self.controller.current_user]
                    
                    with open(self.controller.db_file, 'w') as f:
                        json.dump(users, f, indent=2)
                    
                    messagebox.showinfo("Success", "Account deleted successfully")
                    self.controller.current_user = None
                    self.controller.show_frame("LoginPage")
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete account: {e}")
        else:
            messagebox.showinfo("Cancelled", "Account deletion cancelled")