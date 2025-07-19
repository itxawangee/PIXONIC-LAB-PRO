import json
from datetime import datetime
from tkinter import filedialog

class ProjectManager:
    def __init__(self, controller):
        self.controller = controller
        self.current_project = None
    
    def new_project(self):
        self.current_project = {
            "name": f"Project_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created": datetime.now().isoformat(),
            "images": [],
            "audio": [],
            "settings": {}
        }
    
    def save_project(self, filename=None):
        if not filename:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pmp",
                filetypes=[("Pixonix Project", "*.pmp")]
            )
        
        if filename:
            with open(filename, 'w') as f:
                json.dump(self.current_project, f)
            return True
        return False
    
    def load_project(self, filename=None):
        if not filename:
            filename = filedialog.askopenfilename(
                filetypes=[("Pixonix Project", "*.pmp")]
            )
        
        if filename:
            with open(filename, 'r') as f:
                self.current_project = json.load(f)
            return True
        return False