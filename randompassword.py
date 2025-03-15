import tkinter as tk
from tkinter import ttk
import random
import string
import pyperclip
from PIL import Image, ImageTk
import customtkinter as ctk
import time
import threading

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Generator")
        self.root.geometry("800x800")
        self.root.resizable(False, False)
        
        # Set the theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create a frame for the content
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # App title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Secure Password Generator",
            font=("Big Shoulders Stencil", 24, "bold")
        )
        self.title_label.pack(pady=(20, 30))
        
        # Password purpose
        self.purpose_label = ctk.CTkLabel(
            self.main_frame,
            text="What will this password be used for?",
            font=("Big Shoulders Stencil", 14)
        )
        self.purpose_label.pack(anchor=tk.W, padx=20, pady=(0, 5))
        
        self.purpose_entry = ctk.CTkEntry(
            self.main_frame,
            width=560,
            height=40,
            placeholder_text="e.g., Banking, Social Media, Email..."
        )
        self.purpose_entry.pack(padx=20, pady=(0, 20))
        
        # Password length
        self.length_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.length_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.length_label = ctk.CTkLabel(
            self.length_frame,
            text="Password Length:",
            font=("Roboto", 14)
        )
        self.length_label.pack(side=tk.LEFT)
        
        self.length_value = ctk.CTkLabel(
            self.length_frame,
            text="16",
            font=("Roboto", 14, "bold"),
            width=40
        )
        self.length_value.pack(side=tk.RIGHT)
        
        self.length_slider = ctk.CTkSlider(
            self.main_frame,
            from_=8,
            to=32,
            number_of_steps=24,
            command=self.update_length_value
        )
        self.length_slider.set(16)
        self.length_slider.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Password options
        self.options_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.options_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Variables for checkboxes
        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.numbers_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        
        # Checkboxes
        self.uppercase_check = ctk.CTkCheckBox(
            self.options_frame,
            text="Uppercase (A-Z)",
            variable=self.uppercase_var,
            onvalue=True,
            offvalue=False
        )
        self.uppercase_check.pack(anchor=tk.W, pady=5)
        
        self.lowercase_check = ctk.CTkCheckBox(
            self.options_frame,
            text="Lowercase (a-z)",
            variable=self.lowercase_var,
            onvalue=True,
            offvalue=False
        )
        self.lowercase_check.pack(anchor=tk.W, pady=5)
        
        self.numbers_check = ctk.CTkCheckBox(
            self.options_frame,
            text="Numbers (0-9)",
            variable=self.numbers_var,
            onvalue=True,
            offvalue=False
        )
        self.numbers_check.pack(anchor=tk.W, pady=5)
        
        self.symbols_check = ctk.CTkCheckBox(
            self.options_frame,
            text="Symbols (!@#$%)",
            variable=self.symbols_var,
            onvalue=True,
            offvalue=False
        )
        self.symbols_check.pack(anchor=tk.W, pady=5)
        
        # Generate button
        self.generate_button = ctk.CTkButton(
            self.main_frame,
            text="Generate Password",
            font=("Roboto", 14, "bold"),
            command=self.animate_generate_password,
            height=40
        )
        self.generate_button.pack(pady=20)
        
        # Password display
        self.password_frame = ctk.CTkFrame(self.main_frame)
        self.password_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.password_label = ctk.CTkLabel(
            self.password_frame,
            text="",
            font=("Roboto", 16),
            pady=10
        )
        self.password_label.pack(side=tk.LEFT, padx=10)
        
        self.copy_button = ctk.CTkButton(
            self.password_frame,
            text="Copy",
            command=self.copy_to_clipboard,
            width=80
        )
        self.copy_button.pack(side=tk.RIGHT, padx=10)
        
        # Status message
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Roboto", 12)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Initialize password
        self.current_password = ""
        self.password_frame.pack_forget()  # Hide initially
        
    def update_length_value(self, value):
        self.length_value.configure(text=str(int(value)))
        
    def generate_password(self):
        # Get selected options
        length = int(self.length_slider.get())
        
        # Define character sets based on options
        chars = ""
        if self.uppercase_var.get():
            chars += string.ascii_uppercase
        if self.lowercase_var.get():
            chars += string.ascii_lowercase
        if self.numbers_var.get():
            chars += string.digits
        if self.symbols_var.get():
            chars += string.punctuation
            
        # Ensure at least one option is selected
        if not chars:
            self.status_label.configure(text="Please select at least one option", text_color="red")
            return
            
        # Generate password
        password = ''.join(random.choice(chars) for _ in range(length))
        
        # Update UI
        self.current_password = password
        self.password_label.configure(text=password)
        self.password_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Get purpose
        purpose = self.purpose_entry.get()
        if purpose:
            self.status_label.configure(
                text=f"Password generated for: {purpose}",
                text_color="green"
            )
        else:
            self.status_label.configure(
                text="Password generated successfully!",
                text_color="green"
            )
    
    def animate_generate_password(self):
        # Animate the button
        self.generate_button.configure(state="disabled")
        
        # Create a separate thread for the animation
        threading.Thread(target=self._animate_and_generate, daemon=True).start()
    
    def _animate_and_generate(self):
        # Animate the status message
        self.status_label.configure(text="Generating secure password...")
        
        # Simulate processing time for animation effect
        time.sleep(0.5)
        
        # Use after method to update UI from the main thread
        self.root.after(0, self.generate_password)
        self.root.after(0, lambda: self.generate_button.configure(state="normal"))
    
    def copy_to_clipboard(self):
        if self.current_password:
            pyperclip.copy(self.current_password)
            self.status_label.configure(text="Password copied to clipboard!", text_color="green")
            
            # Flash effect on copy
            original_color = self.password_frame.cget("fg_color")
            self.password_frame.configure(fg_color="#205080")
            self.root.after(150, lambda: self.password_frame.configure(fg_color=original_color))

def main():
    root = ctk.CTk()
    app = PasswordGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()