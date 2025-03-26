import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import requests
import threading
from PIL import Image, ImageTk
import io
import math
import random

class ModernGitHubRepoAnalyzer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("GitHub Repository Analyzer")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Main container with semi-transparent effect
        self.main_container = ctk.CTkFrame(
            self, 
            corner_radius=15, 
            fg_color="#1A1A2E", 
            border_color="#2C2C4E",
            border_width=2
        )
        self.main_container.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.9, anchor='center')

        # Background Canvas for Particle Animation
        self.background_canvas = tk.Canvas(self, bg="#121229", highlightthickness=0)
        self.background_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Create particles for background animation
        self.particles = []
        self.create_dynamic_background()

        # Header
        self.header = ctk.CTkLabel(
            self.main_container, 
            text="GitHub Repository Analyzer", 
            font=("Arial", 24, "bold"),
            text_color="white"
        )
        self.header.pack(pady=(20, 10))

        # Input Frame
        self.input_frame = ctk.CTkFrame(
            self.main_container, 
            fg_color="transparent"
        )
        self.input_frame.pack(pady=20, padx=20, fill='x')

        # Username Input
        self.username_label = ctk.CTkLabel(
            self.input_frame, 
            text="Username:", 
            text_color="white"
        )
        self.username_label.pack(side='left', padx=(0, 10))
        self.username_entry = ctk.CTkEntry(
            self.input_frame, 
            width=250,
            corner_radius=10
        )
        self.username_entry.pack(side='left', padx=10)

        # Repository Input
        self.repo_label = ctk.CTkLabel(
            self.input_frame, 
            text="Repository:", 
            text_color="white"
        )
        self.repo_label.pack(side='left', padx=(20, 10))
        self.repo_entry = ctk.CTkEntry(
            self.input_frame, 
            width=250,
            corner_radius=10
        )
        self.repo_entry.pack(side='left', padx=10)

        # Analyze Button with hover effect
        self.analyze_button = ctk.CTkButton(
            self.input_frame, 
            text="Analyze", 
            command=self.start_analysis,
            corner_radius=10,
            hover_color="#4CAF50"
        )
        self.analyze_button.pack(side='left', padx=10)

        # Results Container
        self.results_container = ctk.CTkScrollableFrame(
            self.main_container, 
            fg_color="#1E1E3C",
            corner_radius=10
        )
        self.results_container.pack(pady=20, padx=20, fill='both', expand=True)

        # Status Label
        self.status_label = ctk.CTkLabel(
            self.main_container, 
            text="", 
            text_color="white"
        )
        self.status_label.pack(pady=10)

        # Start particle animation
        self.animate_particles()

    def create_dynamic_background(self):
        """Create a dynamic moving background of particles"""
        self.particles = []
        for _ in range(100):
            x = random.randint(0, self.winfo_screenwidth())
            y = random.randint(0, self.winfo_screenheight())
            size = random.randint(1, 3)
            speed = random.uniform(0.5, 2)
            direction = random.uniform(0, 2 * math.pi)
            particle = {
                'x': x, 
                'y': y, 
                'size': size, 
                'speed': speed, 
                'direction': direction,
                'color': random.choice(['#2C2C4E', '#3A3A5C', '#4A4A6C'])
            }
            self.particles.append(particle)

    def animate_particles(self):
        """Animate background particles"""
        self.background_canvas.delete('particle')
        for particle in self.particles:
            # Move particle
            particle['x'] += particle['speed'] * math.cos(particle['direction'])
            particle['y'] += particle['speed'] * math.sin(particle['direction'])

            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = self.winfo_screenwidth()
            elif particle['x'] > self.winfo_screenwidth():
                particle['x'] = 0
            if particle['y'] < 0:
                particle['y'] = self.winfo_screenheight()
            elif particle['y'] > self.winfo_screenheight():
                particle['y'] = 0

            # Draw particle
            self.background_canvas.create_oval(
                particle['x'], particle['y'], 
                particle['x'] + particle['size'], particle['y'] + particle['size'], 
                fill=particle['color'], 
                tags='particle',
                stipple='gray50'
            )

        # Schedule next animation frame
        self.after(50, self.animate_particles)

    def start_analysis(self):
        """Start repository analysis in a separate thread"""
        # Clear previous results
        for widget in self.results_container.winfo_children():
            widget.destroy()

        # Show loading animation
        loading_label = ctk.CTkLabel(
            self.results_container, 
            text="Analyzing Repository...", 
            text_color="white"
        )
        loading_label.pack(pady=20)

        # Start analysis in a thread
        threading.Thread(target=self.fetch_repo_data, daemon=True).start()

    def fetch_repo_data(self):
        """Fetch GitHub repository data"""
        try:
            # Get input values
            username = self.username_entry.get()
            repo = self.repo_entry.get()

            # GitHub API headers (replace with your token)
            headers = {
                'Authorization': 'token YOUR_GITHUB_TOKEN',
                'Accept': 'application/vnd.github.v3+json'
            }

            # Fetch repository details
            repo_url = f'https://api.github.com/repos/{username}/{repo}'
            repo_response = requests.get(repo_url, headers=headers)
            repo_data = repo_response.json()

            # Fetch contributors
            contributors_url = f'https://api.github.com/repos/{username}/{repo}/contributors'
            contributors_response = requests.get(contributors_url, headers=headers)
            contributors_data = contributors_response.json()

            # Update UI with results
            self.after(0, self.display_results, repo_data, contributors_data)

        except Exception as e:
            self.after(0, self.show_error, str(e))

    def display_results(self, repo_data, contributors_data):
        """Display repository analysis results"""
        # Clear previous widgets
        for widget in self.results_container.winfo_children():
            widget.destroy()

        # Create info cards with improved styling
        def create_info_card(parent, title, content):
            card = ctk.CTkFrame(
                parent, 
                fg_color="#2C2C4E", 
                corner_radius=10
            )
            card.pack(pady=10, fill='x')

            title_label = ctk.CTkLabel(
                card, 
                text=title, 
                font=("Arial", 16, "bold"),
                text_color="white"
            )
            title_label.pack(pady=(10,5))

            content_label = ctk.CTkLabel(
                card, 
                text=content, 
                text_color="lightgray",
                wraplength=600
            )
            content_label.pack(pady=(0,10))

        # Repository Details
        create_info_card(
            self.results_container, 
            "Repository Details", 
            f"Name: {repo_data.get('full_name', 'N/A')}\n"
            f"Description: {repo_data.get('description', 'No description')}\n"
            f"Language: {repo_data.get('language', 'N/A')}"
        )

        # Statistics
        create_info_card(
            self.results_container, 
            "Repository Statistics", 
            f"Stars: {repo_data.get('stargazers_count', 0)}\n"
            f"Forks: {repo_data.get('forks_count', 0)}\n"
            f"Open Issues: {repo_data.get('open_issues_count', 0)}\n"
            f"Created: {repo_data.get('created_at', 'N/A')[:10]}"
        )

        # Contributors
        contributors_title = ctk.CTkLabel(
            self.results_container, 
            text="Top Contributors", 
            font=("Arial", 18, "bold"),
            text_color="white"
        )
        contributors_title.pack(pady=(20,10))

        # Contributor Cards
        for contributor in contributors_data[:5]:
            contributor_frame = ctk.CTkFrame(
                self.results_container, 
                fg_color="#2C2C4E", 
                corner_radius=10
            )
            contributor_frame.pack(pady=5, fill='x')

            # Fetch avatar
            try:
                avatar_url = contributor.get('avatar_url')
                avatar_response = requests.get(avatar_url)
                avatar_image = Image.open(io.BytesIO(avatar_response.content))
                avatar_image = avatar_image.resize((50, 50), Image.LANCZOS)
                avatar_photo = ImageTk.PhotoImage(avatar_image)

                avatar_label = ctk.CTkLabel(
                    contributor_frame, 
                    image=avatar_photo, 
                    text=""
                )
                avatar_label.image = avatar_photo
                avatar_label.pack(side='left', padx=10, pady=5)
            except:
                pass

            # Contributor details
            details_label = ctk.CTkLabel(
                contributor_frame, 
                text=f"{contributor.get('login', 'N/A')} - {contributor.get('contributions', 0)} contributions",
                text_color="white"
            )
            details_label.pack(side='left', padx=10)

    def show_error(self, error_message):
        """Display error message"""
        # Clear previous widgets
        for widget in self.results_container.winfo_children():
            widget.destroy()

        error_label = ctk.CTkLabel(
            self.results_container, 
            text=f"Error: {error_message}", 
            text_color="red"
        )
        error_label.pack(pady=20)

def main():
    app = ModernGitHubRepoAnalyzer()
    app.mainloop()

if __name__ == "__main__":
    main()