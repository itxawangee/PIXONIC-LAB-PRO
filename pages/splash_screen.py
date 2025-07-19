import tkinter as tk
from tkinter import ttk

class SplashScreen(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.configure(style='TFrame')
        self.create_widgets()
        
        # Automatically proceed to login after delay
        self.after(2500, lambda: controller.show_frame("LoginPage"))
        
    def create_widgets(self):
        """Create splash screen widgets"""
        container = ttk.Frame(self, style='TFrame')
        container.pack(expand=True, fill=tk.BOTH)
        
        # Logo with tagline
        logo_label = ttk.Label(container, text="PIXONIC LAB PRO", 
                              style='Title.TLabel')
        logo_label.pack(pady=50)
        
        tagline_label = ttk.Label(container, 
                                text="Where images sing and sound paints",
                                style='Header.TLabel')
        tagline_label.pack(pady=10)
        
        # Additional creative messaging
        message_label = ttk.Label(container,
                                text="Create. Combine. Control.\nA fusion of visuals and sound",
                                style='Subheader.TLabel',
                                justify=tk.CENTER)
        message_label.pack(pady=20)
        
        # Loading indicator
        progress = ttk.Progressbar(container, orient='horizontal', 
                                  mode='indeterminate', length=300)
        progress.pack(pady=20)
        progress.start(15)
        
        # Footer
        footer = ttk.Frame(container, style='TFrame')
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        ttk.Label(footer, text="© 2023 PIXONIC LAB PRO. All rights reserved.", 
                 style='Subheader.TLabel').pack()