#image resizer

import customtkinter as ctk
from PIL import Image
import os
from pathlib import Path
import threading
from tkinter import filedialog, messagebox
import tkinter.font as tkfont

class ImageResizerApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Bulk Image Resizer")
        self.window.geometry("800x600")
        
        # Use system default font for programming
        self.default_font = ctk.CTkFont(family="Consolas", size=12)
        self.header_font = ctk.CTkFont(family="Consolas", size=20, weight="bold")
        
        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(3, weight=1)
        
        # UI Components
        self.setup_ui()
        
        # State variables
        self.source_folder = ""
        self.output_folder = ""
        self.is_processing = False
    
    def setup_ui(self):
        # Header
        header = ctk.CTkLabel(
            self.window,
            text="Bulk Image Resizer",
            font=self.header_font
        )
        header.grid(row=0, column=0, pady=20, padx=20, sticky="ew")
        
        # Input frame
        input_frame = ctk.CTkFrame(self.window)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        
        # Source folder selection
        ctk.CTkLabel(input_frame, text="Source:", font=self.default_font).grid(row=0, column=0, padx=5, pady=5)
        self.source_label = ctk.CTkLabel(input_frame, text="No folder selected", font=self.default_font)
        self.source_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(
            input_frame,
            text="Browse",
            font=self.default_font,
            command=self.select_source_folder
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Output folder selection
        ctk.CTkLabel(input_frame, text="Output:", font=self.default_font).grid(row=1, column=0, padx=5, pady=5)
        self.output_label = ctk.CTkLabel(input_frame, text="No folder selected", font=self.default_font)
        self.output_label.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(
            input_frame,
            text="Browse",
            font=self.default_font,
            command=self.select_output_folder
        ).grid(row=1, column=2, padx=5, pady=5)
        
        # Resize options frame
        resize_frame = ctk.CTkFrame(self.window)
        resize_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # Width input
        ctk.CTkLabel(resize_frame, text="Width:", font=self.default_font).pack(side="left", padx=5)
        self.width_var = ctk.StringVar(value="1920")
        self.width_entry = ctk.CTkEntry(resize_frame, textvariable=self.width_var, width=100, font=self.default_font)
        self.width_entry.pack(side="left", padx=5)
        
        # Height input
        ctk.CTkLabel(resize_frame, text="Height:", font=self.default_font).pack(side="left", padx=5)
        self.height_var = ctk.StringVar(value="1080")
        self.height_entry = ctk.CTkEntry(resize_frame, textvariable=self.height_var, width=100, font=self.default_font)
        self.height_entry.pack(side="left", padx=5)
        
        # Maintain aspect ratio checkbox
        self.aspect_ratio_var = ctk.BooleanVar(value=True)
        self.aspect_ratio_cb = ctk.CTkCheckBox(
            resize_frame,
            text="Maintain aspect ratio",
            variable=self.aspect_ratio_var,
            font=self.default_font
        )
        self.aspect_ratio_cb.pack(side="left", padx=20)
        
        # Progress frame
        progress_frame = ctk.CTkFrame(self.window)
        progress_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        progress_frame.grid_columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(progress_frame, text="Ready", font=self.default_font)
        self.status_label.grid(row=1, column=0, padx=20, pady=5)
        
        # Process button
        self.process_button = ctk.CTkButton(
            self.window,
            text="Start Processing",
            font=self.default_font,
            command=self.start_processing
        )
        self.process_button.grid(row=4, column=0, pady=20)
    
    def select_source_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder = folder
            self.source_label.configure(text=folder)
    
    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.output_label.configure(text=folder)
    
    def resize_images(self):
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive numbers")
            
            image_files = [f for f in os.listdir(self.source_folder)
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            
            if not image_files:
                messagebox.showwarning("No Images", "No supported image files found in the source folder")
                return
            
            self.progress_bar.set(0)
            total_files = len(image_files)
            
            for i, filename in enumerate(image_files, 1):
                if not self.is_processing:
                    break
                
                input_path = os.path.join(self.source_folder, filename)
                output_path = os.path.join(self.output_folder, filename)
                
                with Image.open(input_path) as img:
                    if self.aspect_ratio_var.get():
                        # Calculate new dimensions maintaining aspect ratio
                        ratio = min(width/img.width, height/img.height)
                        new_width = int(img.width * ratio)
                        new_height = int(img.height * ratio)
                    else:
                        new_width, new_height = width, height
                    
                    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    resized.save(output_path, quality=95, optimize=True)
                
                progress = i / total_files
                self.window.after(0, self.update_progress, progress, f"Processing: {i}/{total_files}")
            
            if self.is_processing:
                self.window.after(0, self.processing_complete)
        
        except Exception as e:
            self.window.after(0, self.processing_error, str(e))
    
    def start_processing(self):
        if not self.source_folder or not self.output_folder:
            messagebox.showwarning("Missing Folders", "Please select both source and output folders")
            return
        
        self.is_processing = True
        self.process_button.configure(text="Cancel", command=self.cancel_processing)
        self.status_label.configure(text="Starting...")
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self.resize_images)
        thread.daemon = True
        thread.start()
    
    def cancel_processing(self):
        self.is_processing = False
        self.process_button.configure(text="Start Processing", command=self.start_processing)
        self.status_label.configure(text="Cancelled")
        self.progress_bar.set(0)
    
    def update_progress(self, progress, status_text):
        self.progress_bar.set(progress)
        self.status_label.configure(text=status_text)
    
    def processing_complete(self):
        self.is_processing = False
        self.process_button.configure(text="Start Processing", command=self.start_processing)
        self.status_label.configure(text="Processing complete!")
    
    def processing_error(self, error_message):
        self.is_processing = False
        self.process_button.configure(text="Start Processing", command=self.start_processing)
        self.status_label.configure(text=f"Error: {error_message}")
        messagebox.showerror("Error", error_message)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ImageResizerApp()
    app.run()
