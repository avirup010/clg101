import customtkinter as ctk
import requests
import json
import random

class Cloud:
    def __init__(self, canvas, x, y, scale=1.0):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.scale = scale
        self.speed = random.uniform(0.5, 1.5)
        self.circles = []

    def create_cloud(self):
        radius = 20 * self.scale
        offsets = [(0, 0), (-20, 5), (20, 5), (-10, -5), (10, -5)]
        for dx, dy in offsets:
            circle = self.canvas.create_oval(
                self.x + dx * self.scale - radius,
                self.y + dy * self.scale - radius,
                self.x + dx * self.scale + radius,
                self.y + dy * self.scale + radius,
                fill='white',
                outline='white'
            )
            self.circles.append(circle)

    def move(self):
        for circle in self.circles:
            self.canvas.move(circle, self.speed, 0)
            coords = self.canvas.coords(circle)
            if coords and coords[2] > self.canvas.winfo_width():
                self.canvas.move(circle, -self.canvas.winfo_width(), 0)

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x400")
        self.root.title("Weather App")
        self.root.resizable(True, True)
        
        self.api_key = "add your own api key"
        
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill='both', expand=True)
        
        self.label = ctk.CTkLabel(self.frame, text="Enter City:")
        self.label.pack()
        
        self.entry = ctk.CTkEntry(self.frame)
        self.entry.pack()
        
        self.button = ctk.CTkButton(self.frame, text="Get Weather", command=self.get_weather)
        self.button.pack()
        
        self.result_label = ctk.CTkLabel(self.frame, text="")
        self.result_label.pack()
        
        self.canvas = ctk.CTkCanvas(self.frame, width=600, height=200, bg='lightblue')
        self.canvas.pack()
        
        self.clouds = [Cloud(self.canvas, random.randint(50, 550), random.randint(50, 150), scale=random.uniform(0.8, 1.2)) for _ in range(3)]
        for cloud in self.clouds:
            cloud.create_cloud()
        self.animate()
        
    def get_weather(self):
        city = self.entry.get()
        if city:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                weather = data['weather'][0]['main']
                temp = data['main']['temp']
                self.result_label.configure(text=f"{weather}, {temp}°C")
            else:
                self.result_label.configure(text="Location not found")
    
    def animate(self):
        for cloud in self.clouds:
            cloud.move()
        self.root.after(50, self.animate)

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    app = WeatherApp(root)
    root.mainloop()
