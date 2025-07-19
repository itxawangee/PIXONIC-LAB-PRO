import tkinter as tk
from app import ProfessionalMediaEditor
import os
from pydub import AudioSegment

# Set path to ffmpeg
AudioSegment.ffmpeg = "C:/ffmpeg/bin/ffmpeg.exe"
if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalMediaEditor(root)
    root.mainloop()