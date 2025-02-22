"""
Movie Scraper
-----------------------
This application provides a gui to search for and display movie information
using the OMDb (Open Movie Database) API. 

Features:
- Search for movies by title
- Display detailed movie information including:
  * Title
  * Year
  * IMDb Rating
  * Runtime
  * Genre
  * Director
  * Actors
  * Plot summary
- Animated loading spinner during API requests
- Smooth fade-in animations for displayed information
- Error handling for failed requests or movies not found

Requirements:
- customtkinter: For modern-looking GUI elements
- requests: For API communication
- PIL: For image handling
- OMDb API key (get one at: http://www.omdbapi.com/apikey.aspx)

Author: Avirup
Date: February 2024
"""
import customtkinter as ctk
import requests
import threading
import time
from PIL import Image
from io import BytesIO
import json
import math  

class AnimatedLabel(ctk.CTkLabel):
    def __init__(self, *args, **kwargs):
        self._current_opacity = 0
        kwargs["text_color"] = "#000000"
        super().__init__(*args, **kwargs)
    
    def fade_in(self, duration=0.5):
        start_time = time.time()
        
        def animation():
            while self._current_opacity < 1:
                progress = (time.time() - start_time) / duration
                self._current_opacity = min(progress, 1)
                color_value = int(self._current_opacity * 255)
                self.configure(text_color=f"#{color_value:02x}{color_value:02x}{color_value:02x}")
                time.sleep(0.016)
                
        threading.Thread(target=animation, daemon=True).start()

class LoadingSpinner(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(fg_color="transparent")
        self.dots = []
        self._create_dots()
        self.is_spinning = False
        
    def _create_dots(self):
        for i in range(8):
            dot = ctk.CTkLabel(
                self,
                text="•",
                font=("Helvetica", 24),
                text_color="#666666"
            )
            dot.grid(row=0, column=i, padx=2)
            self.dots.append(dot)
    
    def start(self):
        self.is_spinning = True
        self._animate()
        
    def stop(self):
        self.is_spinning = False
        
    def _animate(self):
        if not self.is_spinning:
            return
        
        for i, dot in enumerate(self.dots):
            color_val = int(abs(math.sin(time.time() * 3 + i)) * 200)
            dot.configure(text_color=f"#{color_val:02x}{color_val:02x}{color_val:02x}")
        
        self.after(50, self._animate)

class MovieApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Replace with your actual OMDb API key
        self.api_key = "YOUR_OMDB_API_KEY"
        
        self.title("Movie Info Finder")
        self.geometry("800x600")
        self.configure(fg_color="#1a1a1a")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.create_search_frame()
        self.create_content_frame()
        
        self.spinner = LoadingSpinner(self)
        self.spinner.grid(row=2, column=0, pady=20)
        self.spinner.grid_remove()
        
    def create_search_frame(self):
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, pady=20, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter movie name...",
            height=40,
            font=("Helvetica", 16)
        )
        self.search_entry.grid(row=0, column=0, padx=(20, 10), sticky="ew")
        self.search_entry.bind('<Return>', lambda e: self.search_movie())
        
        self.search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            height=40,
            font=("Helvetica", 16),
            command=self.search_movie
        )
        self.search_button.grid(row=0, column=1, padx=(0, 20))
        
    def create_content_frame(self):
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="#242424",
            corner_radius=10
        )
        self.content_frame.grid(row=1, column=0, padx=20, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = AnimatedLabel(
            self.content_frame,
            text="",
            font=("Helvetica", 24, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="w")
        
        self.info_labels = []
        self.info_fields = ["Year:", "Rating:", "Runtime:", "Genre:", "Director:", "Actors:", "Plot:"]
        
        for i, field in enumerate(self.info_fields):
            label = AnimatedLabel(
                self.content_frame,
                text="",
                font=("Helvetica", 14),
                justify="left",
                wraplength=700
            )
            label.grid(row=i+1, column=0, pady=5, padx=20, sticky="w")
            self.info_labels.append(label)
            
    def search_movie(self):
        movie_name = self.search_entry.get()
        if not movie_name:
            return
        
        self.title_label.configure(text="")
        for label in self.info_labels:
            label.configure(text="")
        
        self.spinner.grid()
        self.spinner.start()
        
        threading.Thread(target=self.fetch_movie_data, args=(movie_name,), daemon=True).start()
        
    def fetch_movie_data(self, movie_name):
        try:
            # Make request to OMDb API
            url = f"http://www.omdbapi.com/?t={movie_name}&apikey={self.api_key}"
            response = requests.get(url)
            
            if response.status_code != 200:
                self.after(0, lambda: self.show_error("Failed to fetch data"))
                return
            
            data = response.json()
            
            if data.get('Response') == 'False':
                self.after(0, lambda: self.show_error(data.get('Error', 'Movie not found')))
                return
            
            # Prepare movie info
            movie_info = {
                'title': data.get('Title', 'N/A'),
                'year': data.get('Year', 'N/A'),
                'rating': data.get('imdbRating', 'N/A'),
                'runtime': data.get('Runtime', 'N/A'),
                'genre': data.get('Genre', 'N/A'),
                'director': data.get('Director', 'N/A'),
                'actors': data.get('Actors', 'N/A'),
                'plot': data.get('Plot', 'N/A')
            }
            
            self.after(0, self.update_ui, movie_info)
            
        except Exception as e:
            self.after(0, lambda: self.show_error(f"Error: {str(e)}"))
        finally:
            self.after(0, self.spinner.grid_remove)
            self.after(0, self.spinner.stop)
    
    def update_ui(self, movie_info):
        # Update title
        self.title_label.configure(text=movie_info['title'])
        self.title_label.fade_in()
        
        # Update other information
        info_values = [
            movie_info['year'],
            movie_info['rating'],
            movie_info['runtime'],
            movie_info['genre'],
            movie_info['director'],
            movie_info['actors'],
            movie_info['plot']
        ]
        
        for label, field, value in zip(self.info_labels, self.info_fields, info_values):
            label.configure(text=f"{field} {value}")
            label.fade_in()
    
    def show_error(self, message):
        self.title_label.configure(text="Error")
        self.title_label.fade_in()
        self.info_labels[0].configure(text=message)
        self.info_labels[0].fade_in()

if __name__ == "__main__":
    app = MovieApp()
    app.mainloop()
