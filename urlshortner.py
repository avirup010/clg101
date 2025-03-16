import tkinter as tk
import customtkinter as ctk
import pyperclip
import random
import string
import threading
import time
import re
from PIL import Image, ImageTk
from math import sin, cos, pi

class URLShortener:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern URL Shortener")
        self.root.geometry("650x580")
        self.root.resizable(False, False)
        
        # Set the theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Animation variables
        self.animation_active = False
        self.animation_speed = 0.05
        self.animation_frame = 0
        
        # Create main frame with shadow effect
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create canvas for background animation
        # The canvas needs to be created BEFORE other widgets in the frame
        self.canvas = tk.Canvas(self.main_frame, bg="#212121", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Now we can properly use the lower method to place it behind other elements
        self.canvas.lower()
        
        # Create header with animated title
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.place(relx=0.5, rely=0.05, anchor=tk.N, relwidth=0.9)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="URL Shortener",
            font=("Roboto", 28, "bold")
        )
        self.title_label.pack(pady=(10, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Create short, shareable links instantly",
            font=("Roboto", 14)
        )
        self.subtitle_label.pack(pady=(0, 15))
        
        # URL input area with glow effect
        self.url_frame = ctk.CTkFrame(self.main_frame, fg_color="#242424")
        self.url_frame.place(relx=0.5, rely=0.2, anchor=tk.N, relwidth=0.9, height=110)
        
        self.url_label = ctk.CTkLabel(
            self.url_frame,
            text="Enter your long URL:",
            font=("Roboto", 16)
        )
        self.url_label.pack(anchor=tk.W, padx=20, pady=(15, 10))
        
        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            width=540,
            height=45,
            placeholder_text="https://example.com/very/long/url/that/needs/shortening"
        )
        self.url_entry.pack(padx=20, pady=(0, 15))
        
        # Options frame
        self.options_frame = ctk.CTkFrame(self.main_frame, fg_color="#242424")
        self.options_frame.place(relx=0.5, rely=0.4, anchor=tk.N, relwidth=0.9, height=120)
        
        self.options_label = ctk.CTkLabel(
            self.options_frame,
            text="Customization Options:",
            font=("Roboto", 16)
        )
        self.options_label.pack(anchor=tk.W, padx=20, pady=(15, 10))
        
        # Custom alias option
        self.custom_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.custom_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.custom_var = tk.BooleanVar(value=False)
        self.custom_check = ctk.CTkCheckBox(
            self.custom_frame,
            text="Use custom alias",
            variable=self.custom_var,
            onvalue=True,
            offvalue=False,
            command=self.toggle_custom_alias
        )
        self.custom_check.pack(side=tk.LEFT)
        
        self.custom_entry = ctk.CTkEntry(
            self.custom_frame,
            width=200,
            placeholder_text="your-custom-alias",
            state="disabled"
        )
        self.custom_entry.pack(side=tk.RIGHT, padx=10)
        
        # Shorten button with ripple effect
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.place(relx=0.5, rely=0.55, anchor=tk.N, relwidth=0.9)
        
        self.shorten_button = ctk.CTkButton(
            self.button_frame,
            text="Shorten URL",
            font=("Roboto", 16, "bold"),
            height=50,
            width=200,
            command=self.animate_shortening
        )
        self.shorten_button.pack(pady=15)
        
        # Results area (hidden initially)
        self.results_frame = ctk.CTkFrame(self.main_frame, fg_color="#242424")
        self.results_frame.place(relx=0.5, rely=0.65, anchor=tk.N, relwidth=0.9, height=0)
        
        self.short_url_label = ctk.CTkLabel(
            self.results_frame,
            text="Your shortened URL:",
            font=("Roboto", 16)
        )
        self.short_url_label.pack(anchor=tk.W, padx=20, pady=(15, 10))
        
        self.result_frame = ctk.CTkFrame(self.results_frame, fg_color="#1a1a1a")
        self.result_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.short_url_entry = ctk.CTkEntry(
            self.result_frame,
            width=420,
            height=40,
            font=("Roboto", 14),
            state="readonly"
        )
        self.short_url_entry.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.copy_button = ctk.CTkButton(
            self.result_frame,
            text="Copy",
            width=80,
            command=self.copy_to_clipboard
        )
        self.copy_button.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Statistics frame
        self.stats_frame = ctk.CTkFrame(self.results_frame, fg_color="#1a1a1a")
        self.stats_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        self.original_length_label = ctk.CTkLabel(
            self.stats_frame,
            text="Original Length: ",
            font=("Roboto", 12)
        )
        self.original_length_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.shortened_length_label = ctk.CTkLabel(
            self.stats_frame,
            text="Shortened Length: ",
            font=("Roboto", 12)
        )
        self.shortened_length_label.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Status message
        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.status_frame.place(relx=0.5, rely=0.9, anchor=tk.N, relwidth=0.9)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=("Roboto", 12)
        )
        self.status_label.pack(pady=5)
        
        # Create particles for background animation
        self.particles = []
        for _ in range(30):
            x = random.randint(10, 590)
            y = random.randint(10, 490)
            size = random.randint(1, 3)
            speed = random.uniform(0.5, 1.5)
            angle = random.uniform(0, 2 * pi)
            color = random.choice(["#1f6aa5", "#2a7db5", "#3490c5", "#4ba3d8"])
            
            particle = {
                "x": x,
                "y": y,
                "size": size,
                "speed": speed,
                "angle": angle,
                "color": color,
                "id": None
            }
            self.particles.append(particle)
        
        # Start animations
        self.start_animations()
        
        # Initialize shortened URL
        self.shortened_url = ""
        
    def toggle_custom_alias(self):
        if self.custom_var.get():
            self.custom_entry.configure(state="normal")
        else:
            self.custom_entry.configure(state="disabled")
    
    def start_animations(self):
        self.animate_particles()
        self.pulse_animation()
    
    def animate_particles(self):
        # Clear previous particles
        for particle in self.particles:
            if particle["id"] is not None:
                self.canvas.delete(particle["id"])
        
        # Draw and update particles
        for particle in self.particles:
            # Update position
            particle["x"] += cos(particle["angle"]) * particle["speed"]
            particle["y"] += sin(particle["angle"]) * particle["speed"]
            
            # Bounce off walls
            if particle["x"] < 0 or particle["x"] > 590:
                particle["angle"] = pi - particle["angle"]
            if particle["y"] < 0 or particle["y"] > 490:
                particle["angle"] = -particle["angle"]
            
            # Draw particle
            particle["id"] = self.canvas.create_oval(
                particle["x"], particle["y"],
                particle["x"] + particle["size"], particle["y"] + particle["size"],
                fill=particle["color"], outline=""
            )
        
        # Schedule next frame
        self.root.after(50, self.animate_particles)
    
    def pulse_animation(self):
        # Subtle pulsing effect on the title
        self.animation_frame += 1
        scale = 1.0 + 0.02 * sin(self.animation_frame * 0.1)
        
        self.title_label.configure(
            font=("Roboto", int(28 * scale), "bold")
        )
        
        # Schedule next frame
        self.root.after(100, self.pulse_animation)
    
    def animate_shortening(self):
        # Disable button during animation
        self.shorten_button.configure(state="disabled", text="Processing...")
        
        # Start the ripple effect
        self._start_ripple_effect()
        
        # Create a separate thread for processing
        threading.Thread(target=self._process_url_shortening, daemon=True).start()
    
    def _start_ripple_effect(self):
        # Create ripple effect centered on the button
        button_x = self.button_frame.winfo_x() + self.shorten_button.winfo_x() + self.shorten_button.winfo_width() // 2
        button_y = self.button_frame.winfo_y() + self.shorten_button.winfo_y() + self.shorten_button.winfo_height() // 2
        
        radius = 5
        max_radius = 150
        ripples = []
        
        def create_ripple():
            ripple = self.canvas.create_oval(
                button_x - radius, button_y - radius,
                button_x + radius, button_y + radius,
                outline="#4a8fe7", width=2, fill=""
            )
            ripples.append(ripple)
            
            def expand_ripple(r=radius, opacity=1.0):
                if r < max_radius:
                    # Expand the ripple
                    self.canvas.coords(
                        ripple,
                        button_x - r, button_y - r,
                        button_x + r, button_y + r
                    )
                    
                    # Fade the ripple
                    opacity = max(0, 1.0 - (r / max_radius))
                    width = max(0.5, 2 * opacity)
                    
                    # Update the opacity by changing the color
                    color_val = int(opacity * 255)
                    color = f"#{color_val:02x}{color_val:02x}ff"
                    
                    self.canvas.itemconfig(ripple, width=width, outline=color)
                    
                    # Schedule next animation frame
                    self.root.after(10, lambda: expand_ripple(r + 5, opacity))
                else:
                    # Remove the ripple when done
                    self.canvas.delete(ripple)
                    ripples.remove(ripple)
            
            # Start expanding this ripple
            expand_ripple()
        
        # Create multiple ripples with delay
        create_ripple()
        self.root.after(100, create_ripple)
        self.root.after(200, create_ripple)
    
    def _process_url_shortening(self):
        # Get the URL
        long_url = self.url_entry.get().strip()
        
        # Validate URL
        if not long_url:
            self._update_status("Please enter a URL to shorten", "red")
            self.root.after(0, lambda: self.shorten_button.configure(state="normal", text="Shorten URL"))
            return
        
        if not long_url.startswith(("http://", "https://")):
            long_url = "https://" + long_url
            
        if not self.validate_url(long_url):
            self._update_status("Please enter a valid URL", "red")
            self.root.after(0, lambda: self.shorten_button.configure(state="normal", text="Shorten URL"))
            return
        
        # Simulate processing time for animation effect
        for i in range(5):
            dots = "." * (i % 4)
            self._update_status(f"Processing{dots}", "#4a8fe7")
            time.sleep(0.3)
        
        # Generate a short URL (in real app would call an API)
        try:
            # In a real app, you would use a URL shortening API
            # For this demo, we'll create a simulated short URL
            if self.custom_var.get() and self.custom_entry.get().strip():
                alias = self.custom_entry.get().strip()
            else:
                alias = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            
            # Simulate domain
            shortened_url = f"https://shr.ink/{alias}"
            
            # Update the UI with the result (on the main thread)
            self.root.after(0, lambda: self._show_result(long_url, shortened_url))
        except Exception as e:
            self._update_status(f"Error: {str(e)}", "red")
            self.root.after(0, lambda: self.shorten_button.configure(state="normal", text="Shorten URL"))
    
    def _update_status(self, message, color):
        self.root.after(0, lambda: self.status_label.configure(text=message, text_color=color))
    
    def _show_result(self, long_url, short_url):
        # Store the shortened URL
        self.shortened_url = short_url
        
        # Calculate lengths for statistics
        original_length = len(long_url)
        shortened_length = len(short_url)
        
        # Update statistics
        self.original_length_label.configure(text=f"Original Length: {original_length} chars")
        self.shortened_length_label.configure(text=f"Shortened Length: {shortened_length} chars")
        
        # Update the result entry
        self.short_url_entry.configure(state="normal")
        self.short_url_entry.delete(0, tk.END)
        self.short_url_entry.insert(0, short_url)
        self.short_url_entry.configure(state="readonly")
        
        # Animate the results area appearance
        self._animate_results_reveal()
        
        # Update status message
        percent_shorter = ((original_length - shortened_length) / original_length) * 100
        self.status_label.configure(
            text=f"URL shortened successfully! {percent_shorter:.1f}% shorter",
            text_color="green"
        )
        
        # Re-enable the button
        self.shorten_button.configure(state="normal", text="Shorten URL")
    
    def _animate_results_reveal(self):
        # Get current height of results frame
        current_height = self.results_frame.winfo_height()
        target_height = 180
        
        # If already showing, skip animation
        if current_height >= target_height:
            return
            
        # Animate height increase
        def animate_height(height=0):
            if height < target_height:
                next_height = min(height + 10, target_height)
                self.results_frame.configure(height=next_height)
                self.root.after(10, lambda: animate_height(next_height))
                
                # Add bounce effect at the end
                if next_height >= target_height:
                    self._bounce_effect(self.results_frame)
        
        # Start animation
        animate_height()
    
    def _bounce_effect(self, widget):
        # Create a small bounce effect
        original_height = widget.winfo_height()
        
        def bounce(step=0, direction=1):
            if step < 6:
                # Calculate bounce offset
                if direction > 0:
                    # Expanding
                    height = original_height + (6 - step) * 2
                else:
                    # Contracting
                    height = original_height - (6 - step) * 1
                
                widget.configure(height=height)
                
                # Continue bounce animation
                self.root.after(50, lambda: bounce(step + 1, direction * -1))
        
        # Start bounce
        bounce()
    
    def copy_to_clipboard(self):
        if self.shortened_url:
            # Copy to clipboard
            pyperclip.copy(self.shortened_url)
            
            # Visual feedback animation
            original_color = self.copy_button.cget("fg_color")
            self.copy_button.configure(fg_color="#22a559", text="Copied!")
            
            # Flash effect on the result field
            original_bg = self.result_frame.cget("fg_color")
            self.result_frame.configure(fg_color="#1f3747")
            
            # Reset after animation
            def reset_button():
                self.copy_button.configure(fg_color=original_color, text="Copy")
                self.result_frame.configure(fg_color=original_bg)
                self.status_label.configure(text="URL copied to clipboard!", text_color="green")
                
                # Show floating notification
                self._show_floating_notification("Copied to clipboard!")
            
            self.root.after(800, reset_button)
    
    def _show_floating_notification(self, message):
        # Create floating notification that animates upward and fades
        notification = ctk.CTkLabel(
            self.main_frame,
            text=message,
            font=("Roboto", 12),
            fg_color="#22a559",
            corner_radius=5,
            text_color="white",
            width=150,
            height=30
        )
        
        # Position near the copy button
        notification.place(x=450, y=400)
        
        # Store original y position
        start_y = 400
        
        # Animate the notification
        def animate_notification(frame=0, opacity=1.0, y_pos=start_y):
            if frame < 20:
                # Move upward
                y_pos -= 1
                notification.place(x=450, y=y_pos)
                self.root.after(30, lambda: animate_notification(frame + 1, opacity, y_pos))
            elif opacity > 0:
                # Fade out
                opacity -= 0.1
                # Convert RGB values to hex for fading effect
                r = int(34 * opacity)
                g = int(165 * opacity)
                b = int(89 * opacity)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                notification.configure(fg_color=hex_color)
                self.root.after(30, lambda: animate_notification(frame, opacity, y_pos))
            else:
                # Remove notification
                notification.destroy()
        
        # Start animation
        animate_notification()
    
    def validate_url(self, url):
        # Basic URL validation
        url_pattern = re.compile(
            r'^(?:http|ftp)s?://'  # http://, https://, ftp://, ftps://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return re.match(url_pattern, url) is not None

def main():
    root = ctk.CTk()
    app = URLShortener(root)
    root.mainloop()

if __name__ == "__main__":
    main()