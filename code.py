import os
import shutil
import time
import threading
from pathlib import Path
from tkinter import *
from tkinter import filedialog, ttk, messagebox
import tkinter.font as tkFont
from PIL import Image, ImageTk
import json

class FileOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")
        self.root.geometry("900x600")
        self.root.minsize(800, 550)
        self.root.configure(bg="#f5f5f7")
        
        # Default file mappings
        self.default_mappings = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
            "Documents": [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx", ".csv", ".rtf"],
            "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"],
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".php", ".json"]
        }
        
        # Load custom mappings if exists
        self.config_file = os.path.join(os.path.expanduser("~"), "file_organizer_config.json")
        self.load_config()
        
        # Variables
        self.source_dir = StringVar(value=os.path.expanduser("~"))
        self.status_text = StringVar(value="Ready to organize files")
        self.is_organizing = False
        self.organized_count = 0
        self.total_files = 0
        self.animation_speed = 10
        
        self.create_ui()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.file_mappings = json.load(f)
            else:
                self.file_mappings = self.default_mappings.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.file_mappings = self.default_mappings.copy()
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.file_mappings, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def create_ui(self):
        # Main frame
        self.main_frame = Frame(self.root, bg="#f5f5f7")
        self.main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = Frame(self.main_frame, bg="#f5f5f7")
        header_frame.pack(fill=X, pady=(0, 20))
        
        title_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
        title = Label(header_frame, text="File Organizer", font=title_font, bg="#f5f5f7", fg="#1e1e1e")
        title.pack(side=LEFT)
        
        # Directory selection
        dir_frame = Frame(self.main_frame, bg="#f5f5f7")
        dir_frame.pack(fill=X, pady=10)
        
        dir_label = Label(dir_frame, text="Source Directory:", font=("Helvetica", 12), bg="#f5f5f7", fg="#1e1e1e")
        dir_label.pack(side=LEFT, padx=(0, 10))
        
        dir_entry = Entry(dir_frame, textvariable=self.source_dir, font=("Helvetica", 12), width=50, bd=0, highlightthickness=1, highlightbackground="#d1d1d1")
        dir_entry.pack(side=LEFT, fill=X, expand=True, ipady=8)
        
        browse_button = Button(dir_frame, text="Browse", font=("Helvetica", 10), bg="#007aff", fg="white", bd=0, padx=15, pady=8, 
                              command=self.browse_directory, activebackground="#0069d9", activeforeground="white", cursor="hand2")
        browse_button.pack(side=LEFT, padx=(10, 0))
        
        # File type mappings
        mappings_frame = LabelFrame(self.main_frame, text="File Type Mappings", font=("Helvetica", 12, "bold"), bg="#f5f5f7", fg="#1e1e1e", bd=0)
        mappings_frame.pack(fill=BOTH, expand=True, pady=15)
        
        # Create a canvas with scrollbar for mappings
        canvas_frame = Frame(mappings_frame, bg="#f5f5f7")
        canvas_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = Canvas(canvas_frame, bg="#f5f5f7", highlightthickness=0)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame for mappings inside canvas
        self.mappings_inner_frame = Frame(self.canvas, bg="#f5f5f7")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.mappings_inner_frame, anchor="nw")
        
        # Load the mappings into UI
        self.show_mappings()
        
        # Configure canvas scrolling
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.mappings_inner_frame.bind("<Configure>", self.on_frame_configure)
        
        # Bottom actions
        action_frame = Frame(self.main_frame, bg="#f5f5f7")
        action_frame.pack(fill=X, pady=(15, 0))
        
        add_mapping_button = Button(action_frame, text="Add Mapping", font=("Helvetica", 10), bg="#34c759", fg="white", bd=0, padx=15, pady=8,
                               command=self.add_mapping, activebackground="#2db84c", activeforeground="white", cursor="hand2")
        add_mapping_button.pack(side=LEFT)
        
        reset_button = Button(action_frame, text="Reset to Default", font=("Helvetica", 10), bg="#ff9500", fg="white", bd=0, padx=15, pady=8,
                           command=self.reset_mappings, activebackground="#e68600", activeforeground="white", cursor="hand2")
        reset_button.pack(side=LEFT, padx=(10, 0))
        
        organize_button = Button(action_frame, text="Organize Files", font=("Helvetica", 12, "bold"), bg="#007aff", fg="white", bd=0, padx=20, pady=10,
                               command=self.start_organizing, activebackground="#0069d9", activeforeground="white", cursor="hand2")
        organize_button.pack(side=RIGHT)
        
        # Progress bar
        progress_frame = Frame(self.main_frame, bg="#f5f5f7")
        progress_frame.pack(fill=X, pady=(15, 0))
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient=HORIZONTAL, length=100, mode='determinate')
        self.progress_bar.pack(fill=X)
        
        # Status
        status_frame = Frame(self.main_frame, bg="#f5f5f7")
        status_frame.pack(fill=X, pady=(5, 0))
        
        self.status_label = Label(status_frame, textvariable=self.status_text, font=("Helvetica", 10), bg="#f5f5f7", fg="#666666")
        self.status_label.pack(side=LEFT)
        
        # Apply a modern style to ttk widgets
        style = ttk.Style()
        style.configure("TProgressbar", thickness=10, troughcolor="#f5f5f7", background="#007aff")
    
    def show_mappings(self):
        # Clear existing content
        for widget in self.mappings_inner_frame.winfo_children():
            widget.destroy()
        
        # Add headers
        header_frame = Frame(self.mappings_inner_frame, bg="#f5f5f7")
        header_frame.pack(fill=X, pady=(0, 5))
        
        folder_label = Label(header_frame, text="Folder Name", font=("Helvetica", 11, "bold"), width=15, anchor="w", bg="#f5f5f7", fg="#1e1e1e")
        folder_label.pack(side=LEFT, padx=(5, 10))
        
        extensions_label = Label(header_frame, text="File Extensions", font=("Helvetica", 11, "bold"), anchor="w", bg="#f5f5f7", fg="#1e1e1e")
        extensions_label.pack(side=LEFT, fill=X, expand=True)
        
        actions_label = Label(header_frame, text="Actions", font=("Helvetica", 11, "bold"), width=12, anchor="w", bg="#f5f5f7", fg="#1e1e1e")
        actions_label.pack(side=LEFT, padx=(10, 5))
        
        # Add separator
        separator = Frame(self.mappings_inner_frame, height=1, bg="#d1d1d1")
        separator.pack(fill=X, pady=5)
        
        # Display each mapping
        row_bg_colors = ["#f5f5f7", "#f0f0f2"]  # Alternating row colors
        
        for i, (folder, extensions) in enumerate(self.file_mappings.items()):
            row_frame = Frame(self.mappings_inner_frame, bg=row_bg_colors[i % 2])
            row_frame.pack(fill=X, pady=2)
            
            folder_entry = Entry(row_frame, font=("Helvetica", 11), bd=0, highlightthickness=1, highlightbackground="#d1d1d1")
            folder_entry.insert(0, folder)
            folder_entry.configure(state="readonly", readonlybackground=row_bg_colors[i % 2])
            folder_entry.pack(side=LEFT, padx=(5, 10), ipady=5, fill=Y)
            
            extensions_text = ", ".join(extensions)
            extensions_entry = Entry(row_frame, font=("Helvetica", 11), bd=0, highlightthickness=1, highlightbackground="#d1d1d1")
            extensions_entry.insert(0, extensions_text)
            extensions_entry.configure(state="readonly", readonlybackground=row_bg_colors[i % 2])
            extensions_entry.pack(side=LEFT, padx=(0, 10), ipady=5, fill=BOTH, expand=True)
            
            button_frame = Frame(row_frame, bg=row_bg_colors[i % 2])
            button_frame.pack(side=LEFT, fill=Y)
            
            edit_button = Button(button_frame, text="Edit", font=("Helvetica", 9), bg="#5856d6", fg="white", bd=0, padx=10, pady=3,
                              command=lambda f=folder: self.edit_mapping(f), activebackground="#4a49b8", activeforeground="white", cursor="hand2")
            edit_button.pack(side=LEFT, padx=(0, 5))
            
            delete_button = Button(button_frame, text="Delete", font=("Helvetica", 9), bg="#ff3b30", fg="white", bd=0, padx=10, pady=3,
                                command=lambda f=folder: self.delete_mapping(f), activebackground="#d9342a", activeforeground="white", cursor="hand2")
            delete_button.pack(side=LEFT)
    
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.source_dir.get())
        if directory:
            self.source_dir.set(directory)
    
    def add_mapping(self):
        # Create a popup window
        popup = Toplevel(self.root)
        popup.title("Add New Mapping")
        popup.geometry("400x200")
        popup.resizable(False, False)
        popup.configure(bg="#f5f5f7")
        popup.transient(self.root)
        popup.grab_set()
        
        Label(popup, text="Folder Name:", font=("Helvetica", 11), bg="#f5f5f7", fg="#1e1e1e").pack(anchor=W, padx=20, pady=(20, 5))
        folder_entry = Entry(popup, font=("Helvetica", 11), bd=0, highlightthickness=1, highlightbackground="#d1d1d1", width=40)
        folder_entry.pack(anchor=W, padx=20, ipady=5)
        
        Label(popup, text="File Extensions (comma separated, include dot):", font=("Helvetica", 11), bg="#f5f5f7", fg="#1e1e1e").pack(anchor=W, padx=20, pady=(15, 5))
        extensions_entry = Entry(popup, font=("Helvetica", 11), bd=0, highlightthickness=1, highlightbackground="#d1d1d1", width=40)
        extensions_entry.pack(anchor=W, padx=20, ipady=5)
        
        def save_new_mapping():
            folder = folder_entry.get().strip()
            extensions = [ext.strip() for ext in extensions_entry.get().split(",") if ext.strip()]
            
            if not folder or not extensions:
                messagebox.showerror("Error", "Both folder name and extensions are required!")
                return
            
            # Ensure extensions have dots
            extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]
            
            # Add to mappings
            self.file_mappings[folder] = extensions
            self.save_config()
            self.show_mappings()
            popup.destroy()
        
        button_frame = Frame(popup, bg="#f5f5f7")
        button_frame.pack(fill=X, padx=20, pady=(20, 0))
        
        Button(button_frame, text="Cancel", font=("Helvetica", 10), bg="#e0e0e0", fg="#1e1e1e", bd=0, padx=15, pady=8,
              command=popup.destroy, cursor="hand2").pack(side=LEFT)
        
        Button(button_frame, text="Save", font=("Helvetica", 10, "bold"), bg="#007aff", fg="white", bd=0, padx=15, pady=8,
              command=save_new_mapping, cursor="hand2").pack(side=RIGHT)
    
    def edit_mapping(self, folder):
        extensions = self.file_mappings.get(folder, [])
        
        # Create a popup window
        popup = Toplevel(self.root)
        popup.title(f"Edit Mapping: {folder}")
        popup.geometry("400x200")
        popup.resizable(False, False)
        popup.configure(bg="#f5f5f7")
        popup.transient(self.root)
        popup.grab_set()
        
        Label(popup, text="Folder Name:", font=("Helvetica", 11), bg="#f5f5f7", fg="#1e1e1e").pack(anchor=W, padx=20, pady=(20, 5))
        folder_entry = Entry(popup, font=("Helvetica", 11), bd=0, highlightthickness=1, highlightbackground="#d1d1d1", width=40)
        folder_entry.insert(0, folder)
        folder_entry.pack(anchor=W, padx=20, ipady=5)
        
        Label(popup, text="File Extensions (comma separated, include dot):", font=("Helvetica", 11), bg="#f5f5f7", fg="#1e1e1e").pack(anchor=W, padx=20, pady=(15, 5))
        extensions_entry = Entry(popup, font=("Helvetica", 11), bd=0, highlightthickness=1, highlightbackground="#d1d1d1", width=40)
        extensions_entry.insert(0, ", ".join(extensions))
        extensions_entry.pack(anchor=W, padx=20, ipady=5)
        
        def save_edited_mapping():
            new_folder = folder_entry.get().strip()
            new_extensions = [ext.strip() for ext in extensions_entry.get().split(",") if ext.strip()]
            
            if not new_folder or not new_extensions:
                messagebox.showerror("Error", "Both folder name and extensions are required!")
                return
            
            # Ensure extensions have dots
            new_extensions = [ext if ext.startswith(".") else f".{ext}" for ext in new_extensions]
            
            # Remove old mapping and add new one
            if folder in self.file_mappings:
                del self.file_mappings[folder]
            self.file_mappings[new_folder] = new_extensions
            self.save_config()
            self.show_mappings()
            popup.destroy()
        
        button_frame = Frame(popup, bg="#f5f5f7")
        button_frame.pack(fill=X, padx=20, pady=(20, 0))
        
        Button(button_frame, text="Cancel", font=("Helvetica", 10), bg="#e0e0e0", fg="#1e1e1e", bd=0, padx=15, pady=8,
              command=popup.destroy, cursor="hand2").pack(side=LEFT)
        
        Button(button_frame, text="Save", font=("Helvetica", 10, "bold"), bg="#007aff", fg="white", bd=0, padx=15, pady=8,
              command=save_edited_mapping, cursor="hand2").pack(side=RIGHT)
    
    def delete_mapping(self, folder):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the mapping for '{folder}'?"):
            if folder in self.file_mappings:
                del self.file_mappings[folder]
                self.save_config()
                self.show_mappings()
    
    def reset_mappings(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset to default mappings?"):
            self.file_mappings = self.default_mappings.copy()
            self.save_config()
            self.show_mappings()
    
    def count_files(self, directory):
        file_count = 0
        for _, _, files in os.walk(directory):
            file_count += len(files)
        return file_count
    
    def start_organizing(self):
        if self.is_organizing:
            messagebox.showinfo("Info", "File organization is already in progress")
            return
        
        source_dir = self.source_dir.get()
        if not os.path.isdir(source_dir):
            messagebox.showerror("Error", "Invalid source directory")
            return
        
        # Start organizing in a separate thread
        self.is_organizing = True
        self.organized_count = 0
        self.total_files = self.count_files(source_dir)
        
        if self.total_files == 0:
            messagebox.showinfo("Info", "No files found in the selected directory")
            self.is_organizing = False
            return
        
        self.progress_bar["value"] = 0
        self.status_text.set("Starting to organize files...")
        
        threading.Thread(target=self.organize_files, daemon=True).start()
    
    def organize_files(self):
        source_dir = self.source_dir.get()
        
        try:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    if not self.is_organizing:  # Check if cancelled
                        break
                    
                    file_path = os.path.join(root, file)
                    
                    # Skip files that are not in the root directory
                    if os.path.dirname(file_path) != source_dir:
                        continue
                    
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # Find which folder this file belongs to
                    target_folder = None
                    for folder, extensions in self.file_mappings.items():
                        if file_ext in extensions:
                            target_folder = folder
                            break
                    
                    if target_folder:
                        # Create target folder if it doesn't exist
                        target_dir = os.path.join(source_dir, target_folder)
                        os.makedirs(target_dir, exist_ok=True)
                        
                        # Move file
                        target_path = os.path.join(target_dir, file)
                        
                        # Handle filename conflicts
                        if os.path.exists(target_path):
                            base_name, ext = os.path.splitext(file)
                            counter = 1
                            while os.path.exists(target_path):
                                new_name = f"{base_name}_{counter}{ext}"
                                target_path = os.path.join(target_dir, new_name)
                                counter += 1
                        
                        shutil.move(file_path, target_path)
                        self.organized_count += 1
                        
                        # Update UI
                        self.update_progress()
                        time.sleep(0.05)  # Small delay for animation
            
            # Final update
            self.root.after(0, self.complete_organization, True)
            
        except Exception as e:
            self.root.after(0, self.complete_organization, False, str(e))
    
    def update_progress(self):
        progress = (self.organized_count / self.total_files) * 100 if self.total_files > 0 else 0
        self.root.after(0, lambda: self.progress_bar.configure(value=progress))
        self.root.after(0, lambda: self.status_text.set(f"Organizing files... ({self.organized_count}/{self.total_files})"))
    
    def complete_organization(self, success, error_msg=None):
        self.is_organizing = False
        
        if success:
            self.status_text.set(f"Organization complete! {self.organized_count} files organized.")
            messagebox.showinfo("Complete", f"Successfully organized {self.organized_count} files.")
        else:
            self.status_text.set(f"Error during organization: {error_msg}")
            messagebox.showerror("Error", f"An error occurred: {error_msg}")
        
        # Reset progress bar with animation
        self.animate_progress_reset()
    
    def animate_progress_reset(self):
        current_value = self.progress_bar["value"]
        if current_value > 0:
            new_value = max(0, current_value - self.animation_speed)
            self.progress_bar["value"] = new_value
            self.root.after(10, self.animate_progress_reset)

def main():
    root = Tk()
    app = FileOrganizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()