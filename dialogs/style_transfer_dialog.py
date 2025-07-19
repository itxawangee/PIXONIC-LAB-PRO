import tkinter as tk
from tkinter import ttk

class StyleTransferDialog(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_style = None
        
        self.title("Select Style")
        self.geometry("400x300")
        self.resizable(False, False)
        
        theme = self.controller.themes[self.controller.current_theme]
        self.configure(background=theme['background'])
        
        ttk.Label(self, text="Select Artistic Style", style='Title.TLabel').pack(pady=10)
        
        styles = ["Van Gogh", "Picasso", "Watercolor", "Ukiyo-e", "Abstract"]
        self.style_var = tk.StringVar()
        
        for style in styles:
            ttk.Radiobutton(self, text=style, variable=self.style_var, 
                           value=style).pack(anchor=tk.W, padx=20, pady=5)
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Apply", style='Primary.TButton',
                  command=self.apply_style).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", style='Secondary.TButton',
                  command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def apply_style(self):
        """Set the selected style and close dialog"""
        self.selected_style = self.style_var.get()
        self.destroy()