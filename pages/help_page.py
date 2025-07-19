import tkinter as tk
from tkinter import ttk

class HelpPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create help page widgets"""
        # Header
        header_frame = ttk.Frame(self, style='TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(header_frame, text="Help & Support", style='Title.TLabel').pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Back to Dashboard", style='Secondary.TButton',
                  command=lambda: self.controller.show_frame("DashboardPage")).pack(side=tk.RIGHT)
        
        # Main content
        content_frame = ttk.Frame(self, style='TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Notebook for tabs
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Getting Started tab
        start_tab = ttk.Frame(notebook, style='TFrame')
        notebook.add(start_tab, text="Getting Started")
        
        text = """Welcome to PIXONIC LAB PRO!

To get started:
1. Open an image or audio file from the File menu
2. Use the tools and effects to edit your media
3. Save your work when you're done

For more detailed instructions, please see our documentation."""
        
        help_text = tk.Text(start_tab, wrap=tk.WORD, padx=10, pady=10)
        help_text.insert(tk.END, text)
        help_text.config(state=tk.DISABLED)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # Documentation tab
        doc_tab = ttk.Frame(notebook, style='TFrame')
        notebook.add(doc_tab, text="Documentation")
        
        doc_text = """Full documentation is available. 

Key Features:
- Image editing: Adjust colors, apply filters, crop and resize
- Audio editing: Change speed, pitch, volume, and apply effects
- User accounts: Save your preferences and access from multiple devices"""
        
        doc_display = tk.Text(doc_tab, wrap=tk.WORD, padx=10, pady=10)
        doc_display.insert(tk.END, doc_text)
        doc_display.config(state=tk.DISABLED)
        doc_display.pack(fill=tk.BOTH, expand=True)
        
        # Contact tab
        contact_tab = ttk.Frame(notebook, style='TFrame')
        notebook.add(contact_tab, text="Contact Support")
        
        contact_text = """Need help? Contact our support team:

Email: akrashnoor2508@gmail.com
Phone: +923115459380

Business Hours:
Monday-Friday: 9am-5pm EST"""
        
        contact_display = tk.Text(contact_tab, wrap=tk.WORD, padx=10, pady=10)
        contact_display.insert(tk.END, contact_text)
        contact_display.config(state=tk.DISABLED)
        contact_display.pack(fill=tk.BOTH, expand=True)