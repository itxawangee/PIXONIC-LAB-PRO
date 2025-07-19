import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps, ImageChops
import numpy as np
import pyaudio
import librosa
from scipy.io import wavfile
from scipy import signal
from pydub import AudioSegment
from pydub.utils import which
from dialogs.style_transfer_dialog import StyleTransferDialog

AudioSegment.converter = which("ffmpeg")

class MediaEditorPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Image editing attributes
        self.current_image = None
        self.original_image = None
        self.tk_image = None
        self.crop_mode = False
        self.crop_start = None
        self.crop_rect = None
        
        # Audio editing attributes
        self.audio_file = None
        self.audio_data = None
        self.sample_rate = None
        self.original_audio = None
        self.is_playing = False
        self.p = pyaudio.PyAudio()
        self.stream = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create combined media editor widgets"""
        # Header
        header_frame = ttk.Frame(self, style='TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.title_label = ttk.Label(header_frame, text="Media Editor", style='Title.TLabel')
        self.title_label.pack(side=tk.LEFT)
        
        btn_frame = ttk.Frame(header_frame, style='TFrame')
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="Back to Dashboard", style='Secondary.TButton',
                  command=lambda: self.controller.show_frame("DashboardPage")).pack(side=tk.LEFT, padx=5)
        
        # Mode selector
        self.mode_var = tk.StringVar(value="image")
        mode_frame = ttk.Frame(header_frame)
        mode_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Radiobutton(mode_frame, text="Image", variable=self.mode_var, 
                       value="image", command=self.switch_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Audio", variable=self.mode_var, 
                       value="audio", command=self.switch_mode).pack(side=tk.LEFT)
        
        # Main content area
        main_frame = ttk.Frame(self, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Media display area
        self.media_frame = ttk.Frame(main_frame)
        self.media_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Image canvas
        self.image_canvas = tk.Canvas(self.media_frame, 
                                    bg=self.controller.themes[self.controller.current_theme]['background'])
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Audio waveform canvas
        self.audio_canvas = tk.Canvas(self.media_frame, 
                                     bg=self.controller.themes[self.controller.current_theme]['background'])
        
        # Control panel
        self.control_frame = ttk.Frame(main_frame, width=350, style='TFrame')
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # Create image and audio control panels
        self.create_image_controls()
        self.create_audio_controls()
        
        # Start with image mode
        self.switch_mode()
        
        # Status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_image_controls(self):
        """Create image editing controls"""
        self.image_notebook = ttk.Notebook(self.control_frame)
        
        # File tab
        file_tab = ttk.Frame(self.image_notebook, style='TFrame')
        self.image_notebook.add(file_tab, text="File")
        
        ttk.Button(file_tab, text="Open Image", style='Primary.TButton',
                  command=self.open_image).pack(fill=tk.X, pady=5)
        ttk.Button(file_tab, text="Save Image", style='Success.TButton',
                  command=self.save_image).pack(fill=tk.X, pady=5)
        ttk.Button(file_tab, text="Reset Image", style='Danger.TButton',
                  command=self.reset_image).pack(fill=tk.X, pady=5)
        
        # Basic Adjustments tab
        basic_tab = ttk.Frame(self.image_notebook, style='TFrame')
        self.image_notebook.add(basic_tab, text="Basic")
        
        # Brightness
        ttk.Label(basic_tab, text="Brightness", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.brightness_slider = ttk.Scale(basic_tab, from_=0, to=200, command=self.apply_adjustments)
        self.brightness_slider.set(100)
        self.brightness_slider.pack(fill=tk.X, pady=5)
        
        
        
        # Saturation
        ttk.Label(basic_tab, text="Saturation", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.saturation_slider = ttk.Scale(basic_tab, from_=0, to=200, command=self.apply_adjustments)
        self.saturation_slider.set(100)
        self.saturation_slider.pack(fill=tk.X, pady=5)
        
        # Filters
        ttk.Label(basic_tab, text="Filters", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.filter_var = tk.StringVar()
        self.filter_var.set("None")
        
        filters = [
            ("None", "None"),
            ("Blur", "Blur"),
            ("Sharpen", "Sharpen"),
            ("Emboss", "Emboss"),
            ("Contour", "Contour"),
            ("Black & White", "Black & White")
        ]
        
        for text, mode in filters:
            ttk.Radiobutton(basic_tab, text=text, variable=self.filter_var, 
                          value=mode, command=self.apply_filters).pack(anchor=tk.W, pady=2)
        
        # Advanced tab
        advanced_tab = ttk.Frame(self.image_notebook, style='TFrame')
        self.image_notebook.add(advanced_tab, text="Advanced")
        
        # Vibrance
        ttk.Label(advanced_tab, text="Vibrance:").pack(anchor=tk.W, pady=(10, 0))
        self.vibrance_slider = ttk.Scale(advanced_tab, from_=0, to=200, command=self.apply_adjustments)
        self.vibrance_slider.set(100)
        self.vibrance_slider.pack(fill=tk.X, pady=5)
        
        # Color Tints
        ttk.Label(advanced_tab, text="Red Tint:").pack(anchor=tk.W, pady=(10, 0))
        self.red_slider = ttk.Scale(advanced_tab, from_=0, to=200, command=self.apply_adjustments)
        self.red_slider.set(100)
        self.red_slider.pack(fill=tk.X, pady=5)
        
        ttk.Label(advanced_tab, text="Green Tint:").pack(anchor=tk.W, pady=(10, 0))
        self.green_slider = ttk.Scale(advanced_tab, from_=0, to=200, command=self.apply_adjustments)
        self.green_slider.set(100)
        self.green_slider.pack(fill=tk.X, pady=5)
        
        ttk.Label(advanced_tab, text="Blue Tint:").pack(anchor=tk.W, pady=(10, 0))
        self.blue_slider = ttk.Scale(advanced_tab, from_=0, to=200, command=self.apply_adjustments)
        self.blue_slider.set(100)
        self.blue_slider.pack(fill=tk.X, pady=5)
        
        # Vignette
        ttk.Label(advanced_tab, text="Vignette:").pack(anchor=tk.W, pady=(10, 0))
        self.vignette_slider = ttk.Scale(advanced_tab, from_=0, to=100, command=self.apply_adjustments)
        self.vignette_slider.set(0)
        self.vignette_slider.pack(fill=tk.X, pady=5)
        
        # Tools tab
        tools_tab = ttk.Frame(self.image_notebook, style='TFrame')
        self.image_notebook.add(tools_tab, text="Tools")
        
        # Transform tools
        transform_frame = ttk.LabelFrame(tools_tab, text="Transform", padding=10)
        transform_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(transform_frame, text="Rotate 90°",
                  command=lambda: self.rotate_image(90)).pack(fill=tk.X, pady=2)
        ttk.Button(transform_frame, text="Flip Horizontal",
                  command=lambda: self.flip_image("horizontal")).pack(fill=tk.X, pady=2)
        ttk.Button(transform_frame, text="Flip Vertical",
                  command=lambda: self.flip_image("vertical")).pack(fill=tk.X, pady=2)
        
        # Crop tools
        crop_frame = ttk.LabelFrame(tools_tab, text="Crop", padding=10)
        crop_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(crop_frame, text="Start Crop", style='Primary.TButton',
                  command=self.start_crop).pack(fill=tk.X, pady=2)
        ttk.Button(crop_frame, text="Apply Crop",
                  command=self.apply_crop, state=tk.DISABLED).pack(fill=tk.X, pady=2)
        self.crop_button = ttk.Button(crop_frame, text="Cancel Crop", style='Danger.TButton',
                                    command=self.cancel_crop)
        self.crop_button.pack(fill=tk.X, pady=2)
        self.crop_button.config(state=tk.DISABLED)
        
        # Resolution
        res_frame = ttk.LabelFrame(tools_tab, text="Resolution", padding=10)
        res_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(res_frame, text="Width:").grid(row=0, column=0, sticky='e', padx=5)
        self.width_entry = ttk.Entry(res_frame)
        self.width_entry.grid(row=0, column=1, sticky='ew', padx=5)
        
        ttk.Label(res_frame, text="Height:").grid(row=1, column=0, sticky='e', padx=5)
        self.height_entry = ttk.Entry(res_frame)
        self.height_entry.grid(row=1, column=1, sticky='ew', padx=5)
        
        ttk.Button(res_frame, text="Resize", style='Primary.TButton',
                  command=self.resize_image).grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')
        
        res_frame.grid_columnconfigure(1, weight=1)
        
        # AI Tools tab
        ai_tab = ttk.Frame(self.image_notebook, style='TFrame')
        self.image_notebook.add(ai_tab, text="AI Tools")
        
        ttk.Button(ai_tab, text="AI Enhance Image", style='Primary.TButton',
                  command=self.ai_enhance_image).pack(fill=tk.X, pady=5)
        ttk.Button(ai_tab, text="AI Remove Background", style='Primary.TButton',
                  command=self.ai_remove_background).pack(fill=tk.X, pady=5)
        ttk.Button(ai_tab, text="AI Style Transfer", style='Primary.TButton',
                  command=self.ai_style_transfer).pack(fill=tk.X, pady=5)
        ttk.Button(ai_tab, text="AI Super Resolution", style='Primary.TButton',
                  command=self.ai_super_resolution).pack(fill=tk.X, pady=5)
    
    def create_audio_controls(self):
        """Create audio editing controls"""
        self.audio_notebook = ttk.Notebook(self.control_frame)
        
        # File tab
        file_tab = ttk.Frame(self.audio_notebook, style='TFrame')
        self.audio_notebook.add(file_tab, text="File")
        
        ttk.Button(file_tab, text="Open Audio", style='Primary.TButton',
                  command=self.open_audio).pack(fill=tk.X, pady=5)
        ttk.Button(file_tab, text="Save Audio", style='Success.TButton',
                  command=self.save_audio).pack(fill=tk.X, pady=5)
        ttk.Button(file_tab, text="Reset Audio", style='Danger.TButton',
                  command=self.reset_audio).pack(fill=tk.X, pady=5)
        
        # Playback tab
        playback_tab = ttk.Frame(self.audio_notebook, style='TFrame')
        self.audio_notebook.add(playback_tab, text="Playback")
        
        # Play/pause button
        self.play_button = ttk.Button(playback_tab, text="Play", style='Primary.TButton',
                                    command=self.toggle_playback)
        self.play_button.pack(fill=tk.X, pady=5)
        
        # Stop button
        ttk.Button(playback_tab, text="Stop", style='Danger.TButton',
                  command=self.stop_playback).pack(fill=tk.X, pady=5)
        
        # Volume control
        ttk.Label(playback_tab, text="Volume:").pack(anchor=tk.W, pady=(10, 0))
        self.volume_slider = ttk.Scale(playback_tab, from_=0, to=100, command=self.set_volume)
        self.volume_slider.set(80)
        self.volume_slider.pack(fill=tk.X, pady=5)
        
        # Speed control
        ttk.Label(playback_tab, text="Speed:").pack(anchor=tk.W, pady=(10, 0))
        self.speed_slider = ttk.Scale(playback_tab, from_=50, to=200, command=self.set_speed)
        self.speed_slider.set(100)
        self.speed_slider.pack(fill=tk.X, pady=5)
        
        # Basic Effects tab
        basic_tab = ttk.Frame(self.audio_notebook, style='TFrame')
        self.audio_notebook.add(basic_tab, text="Basic Effects")
        
        ttk.Button(basic_tab, text="Normalize", style='Primary.TButton',
                  command=self.normalize_audio).pack(fill=tk.X, pady=5)
        ttk.Button(basic_tab, text="Fade In", style='Primary.TButton',
                  command=lambda: self.fade_audio("in")).pack(fill=tk.X, pady=5)
        ttk.Button(basic_tab, text="Fade Out", style='Primary.TButton',
                  command=lambda: self.fade_audio("out")).pack(fill=tk.X, pady=5)
        ttk.Button(basic_tab, text="Reverse", style='Primary.TButton',
                  command=self.reverse_audio).pack(fill=tk.X, pady=5)
        
        # Advanced Effects tab
        advanced_tab = ttk.Frame(self.audio_notebook, style='TFrame')
        self.audio_notebook.add(advanced_tab, text="Advanced Effects")
        
        ttk.Button(advanced_tab, text="Echo", style='Primary.TButton',
                  command=self.add_echo).pack(fill=tk.X, pady=5)
        ttk.Button(advanced_tab, text="Reverb", style='Primary.TButton',
                  command=self.add_reverb).pack(fill=tk.X, pady=5)
        
        # AI Tools tab
        ai_tab = ttk.Frame(self.audio_notebook, style='TFrame')
        self.audio_notebook.add(ai_tab, text="AI Tools")
        
        ttk.Button(ai_tab, text="AI Enhance Audio", style='Primary.TButton',
                  command=self.ai_enhance_audio).pack(fill=tk.X, pady=5)
        ttk.Button(ai_tab, text="AI Noise Reduction", style='Primary.TButton',
                  command=self.ai_noise_reduction).pack(fill=tk.X, pady=5)
        ttk.Button(ai_tab, text="AI Voice Enhancement", style='Primary.TButton',
                  command=self.ai_voice_enhancement).pack(fill=tk.X, pady=5)
    
    def switch_mode(self):
        """Switch between image and audio editing modes"""
        mode = self.mode_var.get()
        
        if mode == "image":
            self.title_label.config(text="Image Editor")
            self.audio_canvas.pack_forget()
            self.image_canvas.pack(fill=tk.BOTH, expand=True)
            self.audio_notebook.pack_forget()
            self.image_notebook.pack(fill=tk.BOTH, expand=True)
        else:
            self.title_label.config(text="Audio Editor")
            self.image_canvas.pack_forget()
            self.audio_canvas.pack(fill=tk.BOTH, expand=True)
            self.image_notebook.pack_forget()
            self.audio_notebook.pack(fill=tk.BOTH, expand=True)
    
    # Image editing methods
    def open_image(self):
        """Open image file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")]
        )
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.current_image = self.original_image.copy()
                self.display_image()
                self.status_var.set(f"Opened: {os.path.basename(file_path)}")
                
                # Update resolution entries
                self.width_entry.delete(0, tk.END)
                self.width_entry.insert(0, str(self.current_image.width))
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(self.current_image.height))
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {e}")
    
    def save_image(self):
        """Save image file"""
        if self.current_image:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
            )
            if file_path:
                try:
                    self.current_image.save(file_path)
                    self.status_var.set(f"Saved: {os.path.basename(file_path)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save image: {e}")
    
    def reset_image(self):
        """Reset image to original"""
        if self.original_image:
            self.current_image = self.original_image.copy()
            self.display_image()
            self.brightness_slider.set(100)
            self.contrast_slider.set(100)
            self.saturation_slider.set(100)
            self.vibrance_slider.set(100)
            self.red_slider.set(100)
            self.green_slider.set(100)
            self.blue_slider.set(100)
            self.vignette_slider.set(0)
            self.filter_var.set("None")
            
            # Update resolution entries
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(self.current_image.width))
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(self.current_image.height))
            
            self.status_var.set("Image reset to original")
    
    def display_image(self):
        """Display image on canvas"""
        if self.current_image:
            # Calculate ratio to fit in canvas
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:  # If canvas not yet sized
                canvas_width = 800
                canvas_height = 600
            
            img_ratio = self.current_image.width / self.current_image.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                new_width = canvas_width
                new_height = int(canvas_width / img_ratio)
            else:
                new_height = canvas_height
                new_width = int(canvas_height * img_ratio)
            
            # Resize for display
            display_image = self.current_image.resize((new_width, new_height), Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(display_image)
            
            # Clear canvas and display image
            self.image_canvas.delete("all")
            self.image_canvas.create_image(canvas_width//2, canvas_height//2, image=self.tk_image, anchor=tk.CENTER)
            
            # If in crop mode, show crop rectangle
            if self.crop_mode and self.crop_rect:
                self.image_canvas.create_rectangle(self.crop_rect, outline='red', width=2, tags="crop_rect")
    
    def apply_adjustments(self, event=None):
        """Apply image adjustments"""
        if self.current_image:
            try:
                # Start with original image
                img = self.original_image.copy()
                
                # Apply brightness
                brightness = self.brightness_slider.get() / 100
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)
                
                # Apply contrast
                contrast = self.contrast_slider.get() / 100
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)
                
                # Apply saturation
                saturation = self.saturation_slider.get() / 100
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(saturation)
                
                # Apply vibrance (more complex - boost muted colors)
                vibrance = self.vibrance_slider.get() / 100
                if vibrance != 1.0:
                    img = self.apply_vibrance(img, vibrance)
                
                # Apply color tints
                red = self.red_slider.get() / 100
                green = self.green_slider.get() / 100
                blue = self.blue_slider.get() / 100
                if red != 1.0 or green != 1.0 or blue != 1.0:
                    img = self.apply_tint(img, red, green, blue)
                
                # Apply vignette
                vignette = self.vignette_slider.get()
                if vignette > 0:
                    img = self.apply_vignette(img, vignette)
                
                # Update current image and display
                self.current_image = img
                self.display_image()
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not apply adjustments: {e}")
    
    def apply_vibrance(self, img, amount):
        """Enhance muted colors more than already saturated ones"""
        # Convert to HSV color space
        hsv = img.convert('HSV')
        h, s, v = hsv.split()
        
        # Enhance saturation based on current saturation
        s = s.point(lambda x: int(x * (1 + (amount - 1) * (1 - x / 255))))
        
        # Convert back to RGB
        enhanced_hsv = Image.merge('HSV', (h, s, v))
        return enhanced_hsv.convert('RGB')
    
    def apply_tint(self, img, red, green, blue):
        """Apply color tint to image"""
        # Split into RGB channels
        r, g, b = img.split()
        
        # Adjust each channel
        r = r.point(lambda x: x * red)
        g = g.point(lambda x: x * green)
        b = b.point(lambda x: x * blue)
        
        # Merge back
        return Image.merge('RGB', (r, g, b))
    
    def apply_vignette(self, img, amount):
        """Apply vignette effect to image"""
        # Create mask
        width, height = img.size
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        X, Y = np.meshgrid(x, y)
        mask = 1 - np.sqrt(X**2 + Y**2) * (amount / 100)
        mask = np.clip(mask, 0, 1)
        
        # Convert to PIL image
        mask_img = Image.fromarray((mask * 255).astype(np.uint8))
        
        # Apply mask to each channel
        r, g, b = img.split()
        r = ImageChops.multiply(r, mask_img)
        g = ImageChops.multiply(g, mask_img)
        b = ImageChops.multiply(b, mask_img)
        
        return Image.merge('RGB', (r, g, b))
    
    def apply_filters(self):
        """Apply selected filter"""
        if self.current_image:
            try:
                img = self.current_image.copy()
                selected_filter = self.filter_var.get()
                
                if selected_filter == "Blur":
                    img = img.filter(ImageFilter.BLUR)
                elif selected_filter == "Sharpen":
                    img = img.filter(ImageFilter.SHARPEN)
                elif selected_filter == "Emboss":
                    img = img.filter(ImageFilter.EMBOSS)
                elif selected_filter == "Contour":
                    img = img.filter(ImageFilter.CONTOUR)
                elif selected_filter == "Black & White":
                    img = img.convert('L').convert('RGB')
                
                self.current_image = img
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error", f"Could not apply filter: {e}")
    
    def rotate_image(self, degrees):
        """Rotate image by specified degrees"""
        if self.current_image:
            self.current_image = self.current_image.rotate(degrees, expand=True)
            self.display_image()
            
            # Update resolution entries
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(self.current_image.width))
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(self.current_image.height))
    
    def flip_image(self, direction):
        """Flip image horizontally or vertically"""
        if self.current_image:
            if direction == "horizontal":
                self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
            else:
                self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
            self.display_image()
    
    def start_crop(self):
        """Start crop mode"""
        if self.current_image:
            self.crop_mode = True
            self.crop_button.config(state=tk.NORMAL)
            self.image_canvas.bind("<Button-1>", self.crop_start)
            self.image_canvas.bind("<B1-Motion>", self.crop_move)
            self.image_canvas.bind("<ButtonRelease-1>", self.crop_end)
            self.status_var.set("Crop mode: Click and drag to select area")
    
    def crop_start(self, event):
        """Start crop selection"""
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        
        if hasattr(self, 'crop_rect'):
            self.image_canvas.delete("crop_rect")
        
        self.crop_rect = (self.crop_start_x, self.crop_start_y, event.x, event.y)
        self.image_canvas.create_rectangle(self.crop_rect, outline='red', width=2, tags="crop_rect")
    
    def crop_move(self, event):
        """Update crop selection"""
        if self.crop_start_x and self.crop_start_y:
            self.crop_rect = (self.crop_start_x, self.crop_start_y, event.x, event.y)
            self.image_canvas.delete("crop_rect")
            self.image_canvas.create_rectangle(self.crop_rect, outline='red', width=2, tags="crop_rect")
    
    def apply_crop(self):
        """Apply crop to image"""
        if self.current_image and self.crop_rect:
            try:
                # Get canvas dimensions
                canvas_width = self.image_canvas.winfo_width()
                canvas_height = self.image_canvas.winfo_height()
                
                # Calculate ratio between canvas and actual image
                img_width, img_height = self.current_image.size
                x_ratio = img_width / canvas_width
                y_ratio = img_height / canvas_height
                
                # Convert canvas coordinates to image coordinates
                x1 = int(self.crop_rect[0] * x_ratio)
                y1 = int(self.crop_rect[1] * y_ratio)
                x2 = int(self.crop_rect[2] * x_ratio)
                y2 = int(self.crop_rect[3] * y_ratio)
                
                # Ensure coordinates are within image bounds
                x1 = max(0, min(x1, img_width))
                x2 = max(0, min(x2, img_width))
                y1 = max(0, min(y1, img_height))
                y2 = max(0, min(y2, img_height))
                
                # Ensure proper order (x1 < x2, y1 < y2)
                if x1 > x2:
                    x1, x2 = x2, x1
                if y1 > y2:
                    y1, y2 = y2, y1
                
                # Crop the image
                self.current_image = self.current_image.crop((x1, y1, x2, y2))
                
                # Reset crop mode
                self.crop_mode = False
                self.crop_button.config(state=tk.DISABLED)
                self.image_canvas.unbind("<Button-1>")
                self.image_canvas.unbind("<B1-Motion>")
                self.image_canvas.unbind("<ButtonRelease-1>")
                self.image_canvas.delete("crop_rect")
                self.crop_rect = None
                self.crop_start_x = None
                self.crop_start_y = None
                
                # Update display and resolution entries
                self.display_image()
                self.width_entry.delete(0, tk.END)
                self.width_entry.insert(0, str(self.current_image.width))
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(self.current_image.height))
                
                self.status_var.set("Image cropped")
            except Exception as e:
                messagebox.showerror("Error", f"Could not crop image: {e}")
    
    def crop_end(self, event):
        """End crop selection (same as apply for simplicity)"""
        self.apply_crop()
    
    def cancel_crop(self):
        """Cancel crop operation"""
        self.crop_mode = False
        self.crop_button.config(state=tk.DISABLED)
        self.image_canvas.unbind("<Button-1>")
        self.image_canvas.unbind("<B1-Motion>")
        self.image_canvas.unbind("<ButtonRelease-1>")
        self.image_canvas.delete("crop_rect")
        self.crop_rect = None
        self.crop_start_x = None
        self.crop_start_y = None
        self.status_var.set("Crop cancelled")
    
    def resize_image(self):
        """Resize image to specified dimensions"""
        if self.current_image:
            try:
                width = int(self.width_entry.get())
                height = int(self.height_entry.get())
                
                if width <= 0 or height <= 0:
                    messagebox.showerror("Error", "Width and height must be positive numbers")
                    return
                
                self.current_image = self.current_image.resize((width, height), Image.LANCZOS)
                self.display_image()
                self.status_var.set(f"Image resized to {width}x{height}")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for width and height")
            except Exception as e:
                messagebox.showerror("Error", f"Could not resize image: {e}")
    
    def ai_enhance_image(self):
        """Use AI to enhance image quality"""
        if not self.current_image:
            messagebox.showerror("Error", "No image to enhance")
            return
        
        try:
            # In a real app, this would call an actual AI service API
            messagebox.showinfo("AI Enhancement", "Applying AI enhancement...")
            
            # Simulate enhancement with sharpening and color boost
            enhanced = self.current_image.filter(ImageFilter.SHARPEN)
            enhancer = ImageEnhance.Color(enhanced)
            enhanced = enhancer.enhance(1.2)
            
            self.current_image = enhanced
            self.display_image()
            self.status_var.set("Applied AI enhancement")
            
        except Exception as e:
            messagebox.showerror("Error", f"AI enhancement failed: {e}")
    
    def ai_remove_background(self):
        """Use AI to remove image background"""
        if not self.current_image:
            messagebox.showerror("Error", "No image to process")
            return
        
        try:
            # In a real app, this would call an actual AI service API
            messagebox.showinfo("Background Removal", "Applying AI background removal...")
            
            # Convert to RGBA if not already
            if self.current_image.mode != 'RGBA':
                self.current_image = self.current_image.convert('RGBA')
            
            # Create a mask where darker pixels become transparent
            datas = self.current_image.getdata()
            new_data = []
            for item in datas:
                # Change pixels with high brightness to transparent
                if item[0] > 200 and item[1] > 200 and item[2] > 200:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            
            self.current_image.putdata(new_data)
            self.display_image()
            self.status_var.set("Applied AI background removal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Background removal failed: {e}")
    
    def ai_style_transfer(self):
        """Apply artistic style to image using AI"""
        if not self.current_image:
            messagebox.showerror("Error", "No image to process")
            return
        
        try:
            # Show style selection dialog
            dialog = StyleTransferDialog(self, self.controller)
            self.wait_window(dialog)
            
            if dialog.selected_style:
                messagebox.showinfo("Style Transfer", f"Applying {dialog.selected_style} style...")
                
                # In a real app, this would call an actual AI service API
                # Here we simulate style transfer with color adjustments
                if dialog.selected_style == "Van Gogh":
                    # Apply yellow/blue color shift
                    r, g, b = self.current_image.split()
                    r = r.point(lambda x: x * 1.1)
                    g = g.point(lambda x: x * 0.9)
                    b = b.point(lambda x: x * 1.2)
                    styled = Image.merge("RGB", (r, g, b))
                elif dialog.selected_style == "Picasso":
                    # Apply cubist-like effect (simplified)
                    styled = self.current_image.filter(ImageFilter.CONTOUR)
                else:  # Default to watercolor
                    styled = self.current_image.filter(ImageFilter.SMOOTH_MORE)
                
                self.current_image = styled
                self.display_image()
                self.status_var.set(f"Applied {dialog.selected_style} style")
                
        except Exception as e:
            messagebox.showerror("Error", f"Style transfer failed: {e}")
    
    def ai_super_resolution(self):
        """Use AI to increase image resolution"""
        if not self.current_image:
            messagebox.showerror("Error", "No image to enhance")
            return
        
        try:
            # In a real app, this would call an actual AI service API
            messagebox.showinfo("Super Resolution", "Applying AI super resolution...")
            
            # Simulate super resolution by upscaling with LANCZOS
            width, height = self.current_image.size
            upscaled = self.current_image.resize((width*2, height*2), Image.LANCZOS)
            
            self.current_image = upscaled
            self.display_image()
            
            # Update resolution entries
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(self.current_image.width))
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(self.current_image.height))
            
            self.status_var.set("Applied AI super resolution")
            
        except Exception as e:
            messagebox.showerror("Error", f"Super resolution failed: {e}")
    
    # Audio editing methods
    def open_audio(self):
        """Open audio file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.wav;*.mp3;*.ogg;*.flac")]
        )
        if file_path:
            try:
                # Read audio file
                if file_path.lower().endswith('.mp3'):
                    audio = AudioSegment.from_mp3(file_path)
                    self.audio_data = np.array(audio.get_array_of_samples())
                    self.sample_rate = audio.frame_rate
                else:
                    self.sample_rate, self.audio_data = wavfile.read(file_path)
                
                # Convert stereo to mono if needed
                if len(self.audio_data.shape) > 1:
                    self.audio_data = np.mean(self.audio_data, axis=1)
                
                # Store original for reset
                self.original_audio = self.audio_data.copy()
                self.audio_file = file_path
                
                # Display waveform
                self.display_waveform()
                self.status_var.set(f"Opened: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open audio file: {e}")
    
    def save_audio(self):
        """Save audio file"""
        if self.audio_data is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[("WAV", "*.wav"), ("MP3", "*.mp3")]
            )
            if file_path:
                try:
                    if file_path.lower().endswith('.mp3'):
                        # Convert numpy array to AudioSegment
                        audio_segment = AudioSegment(
                            self.audio_data.tobytes(), 
                            frame_rate=self.sample_rate,
                            sample_width=self.audio_data.dtype.itemsize, 
                            channels=1
                        )
                        audio_segment.export(file_path, format="mp3")
                    else:
                        wavfile.write(file_path, self.sample_rate, self.audio_data)
                    
                    self.status_var.set(f"Saved: {os.path.basename(file_path)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save audio file: {e}")
    
    def reset_audio(self):
        """Reset audio to original"""
        if self.original_audio is not None:
            self.audio_data = self.original_audio.copy()
            self.display_waveform()
            self.status_var.set("Audio reset to original")
    
    def display_waveform(self):
        """Display audio waveform on canvas"""
        if self.audio_data is not None:
            self.audio_canvas.delete("all")
            
            # Get canvas dimensions
            width = self.audio_canvas.winfo_width()
            height = self.audio_canvas.winfo_height()
            
            if width <= 1 or height <= 1:  # If canvas not yet sized
                width = 800
                height = 200
            
            # Downsample for display
            step = max(1, len(self.audio_data) // width)
            samples = self.audio_data[::step]
            
            # Normalize to canvas height
            max_val = np.max(np.abs(samples))
            if max_val > 0:
                samples = samples / max_val * (height / 2 - 10)
            
            # Draw waveform
            mid_y = height // 2
            for i in range(1, len(samples)):
                x1 = (i-1) * (width / len(samples))
                y1 = mid_y - samples[i-1]
                x2 = i * (width / len(samples))
                y2 = mid_y - samples[i]
                self.audio_canvas.create_line(x1, y1, x2, y2, fill="blue")
    
    def toggle_playback(self):
        """Toggle audio playback"""
        if self.audio_data is None:
            return
            
        if self.is_playing:
            self.stop_playback()
        else:
            self.start_playback()
    
    def start_playback(self):
        """Start audio playback"""
        if self.audio_data is not None and not self.is_playing:
            self.is_playing = True
            self.play_button.config(text="Pause")
            
            # Open stream
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                output=True
            )
            
            # Play audio in chunks
            chunk_size = 1024
            self.playback_pos = 0
            self.play_audio_chunk(chunk_size)
    
    def play_audio_chunk(self, chunk_size):
        """Play a chunk of audio data"""
        if self.is_playing and self.playback_pos < len(self.audio_data):
            chunk = self.audio_data[self.playback_pos:self.playback_pos + chunk_size]
            self.stream.write(chunk.tobytes())
            self.playback_pos += chunk_size
            
            # Update playback position on waveform
            self.update_playback_position()
            
            # Schedule next chunk
            self.after(10, lambda: self.play_audio_chunk(chunk_size))
        else:
            self.stop_playback()
    
    def update_playback_position(self):
        """Update playback position indicator on waveform"""
        if self.audio_data is not None:
            self.audio_canvas.delete("position")
            
            width = self.audio_canvas.winfo_width()
            if width <= 1:
                width = 800
                
            pos_x = (self.playback_pos / len(self.audio_data)) * width
            self.audio_canvas.create_line(pos_x, 0, pos_x, self.audio_canvas.winfo_height(), 
                                  fill="red", tags="position", width=2)
    
    def stop_playback(self):
        """Stop audio playback"""
        if self.is_playing:
            self.is_playing = False
            self.play_button.config(text="Play")
            
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
    
    def set_volume(self, value):
        """Set playback volume"""
        # This would adjust the volume of the audio data before playback
        pass
    
    def set_speed(self, value):
        """Set playback speed"""
        # This would adjust the playback speed
        pass
    
    def normalize_audio(self):
        """Normalize audio to maximum volume"""
        if self.audio_data is not None:
            max_val = np.max(np.abs(self.audio_data))
            if max_val > 0:
                self.audio_data = (self.audio_data / max_val) * 32767  # For 16-bit audio
                self.display_waveform()
                self.status_var.set("Audio normalized")
    
    def fade_audio(self, fade_type):
        """Apply fade in or fade out effect"""
        if self.audio_data is not None:
            length = len(self.audio_data)
            fade_samples = min(length // 10, 44100)  # 1 second or 10% of audio
            
            if fade_type == "in":
                # Fade in
                fade = np.linspace(0, 1, fade_samples)
                self.audio_data[:fade_samples] = self.audio_data[:fade_samples] * fade
            else:
                # Fade out
                fade = np.linspace(1, 0, fade_samples)
                self.audio_data[-fade_samples:] = self.audio_data[-fade_samples:] * fade
            
            self.display_waveform()
            self.status_var.set(f"Applied {fade_type} fade")
    
    def reverse_audio(self):
        """Reverse audio"""
        if self.audio_data is not None:
            self.audio_data = np.flip(self.audio_data)
            self.display_waveform()
            self.status_var.set("Audio reversed")
    
    def add_echo(self):
        """Add echo effect to audio"""
        if self.audio_data is not None:
            try:
                echo_delay = int(0.2 * self.sample_rate)  # 200ms delay
                echo = np.zeros_like(self.audio_data)
                echo[echo_delay:] = self.audio_data[:-echo_delay] * 0.5
                self.audio_data = (self.audio_data + echo).astype(np.int16)
                
                # Ensure we don't clip
                max_val = np.max(np.abs(self.audio_data))
                if max_val > 32767:
                    self.audio_data = (self.audio_data / max_val) * 32767
                
                self.display_waveform()
                self.status_var.set("Added echo effect")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add echo: {e}")
    
    def add_reverb(self):
        """Add reverb effect to audio"""
        if self.audio_data is not None:
            try:
                # Simple reverb simulation with multiple echoes
                reverb = np.zeros_like(self.audio_data)
                delays = [int(d * self.sample_rate) for d in [0.02, 0.04, 0.08, 0.16]]
                gains = [0.7, 0.5, 0.3, 0.1]
                
                for delay, gain in zip(delays, gains):
                    reverb[delay:] += self.audio_data[:-delay] * gain
                
                self.audio_data = (self.audio_data + reverb).astype(np.int16)
                
                # Ensure we don't clip
                max_val = np.max(np.abs(self.audio_data))
                if max_val > 32767:
                    self.audio_data = (self.audio_data / max_val) * 32767
                
                self.display_waveform()
                self.status_var.set("Added reverb effect")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add reverb: {e}")
    
    def ai_enhance_audio(self):
        """Use AI to enhance audio quality"""
        if self.audio_data is None:
            messagebox.showerror("Error", "No audio to enhance")
            return
        
        try:
            # In a real app, this would call an actual AI service API
            messagebox.showinfo("AI Enhancement", "Applying AI audio enhancement...")
            
            # Simulate enhancement with some processing
            enhanced = librosa.effects.preemphasis(self.audio_data.astype(np.float32))
            
            # Normalize
            max_val = np.max(np.abs(enhanced))
            if max_val > 0:
                enhanced = (enhanced / max_val) * 32767
            
            self.audio_data = enhanced.astype(np.int16)
            self.display_waveform()
            self.status_var.set("Applied AI audio enhancement")
            
        except Exception as e:
            messagebox.showerror("Error", f"AI enhancement failed: {e}")
    
    def ai_noise_reduction(self):
        """Use AI to reduce background noise"""
        if self.audio_data is None:
            messagebox.showerror("Error", "No audio to process")
            return
        
        try:
            # In a real app, this would call an actual AI service API
            messagebox.showinfo("Noise Reduction", "Applying AI noise reduction...")
            
            # Simulate noise reduction with a simple filter
            b, a = signal.butter(5, 0.1, 'highpass')
            filtered = signal.filtfilt(b, a, self.audio_data)
            
            self.audio_data = filtered.astype(np.int16)
            self.display_waveform()
            self.status_var.set("Applied AI noise reduction")
            
        except Exception as e:
            messagebox.showerror("Error", f"Noise reduction failed: {e}")
    
    def ai_voice_enhancement(self):
        """Use AI to enhance voice in audio"""
        if self.audio_data is None:
            messagebox.showerror("Error", "No audio to process")
            return
        
        try:
            # In a real app, this would call an actual AI service API
            messagebox.showinfo("Voice Enhancement", "Applying AI voice enhancement...")
            
            # Simulate voice enhancement with bandpass filter
            b, a = signal.butter(5, [300/(self.sample_rate/2), 3000/(self.sample_rate/2)], 'bandpass')
            filtered = signal.filtfilt(b, a, self.audio_data)
            
            self.audio_data = filtered.astype(np.int16)
            self.display_waveform()
            self.status_var.set("Applied AI voice enhancement")
            
        except Exception as e:
            messagebox.showerror("Error", f"Voice enhancement failed: {e}")