import time
import tkinter as tk
import customtkinter as ctk
import math
from threading import Thread
import pygame
import random

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("400x450")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize Pygame for smooth animation and sound
        pygame.init()
        pygame.mixer.init()
        self.canvas = tk.Canvas(root, width=250, height=250, bg="black", highlightthickness=0)
        self.canvas.pack(pady=20)
        
        self.work_time = tk.IntVar(value=25)
        self.break_time = tk.IntVar(value=5)
        self.time_left = self.work_time.get() * 60
        
        self.running = False
        self.paused = False
        
        self.timer_label = ctk.CTkLabel(root, text=f"{self.work_time.get()}:00", font=("Arial", 30))
        self.timer_label.pack(pady=10)
        
        self.progress = ctk.CTkProgressBar(root, width=300)
        self.progress.set(1)
        self.progress.pack(pady=10)
        
        # Controls
        self.start_btn = ctk.CTkButton(root, text="Start", command=self.start_timer)
        self.start_btn.pack(pady=5)
        self.pause_btn = ctk.CTkButton(root, text="Pause", command=self.pause_timer)
        self.pause_btn.pack(pady=5)
        self.reset_btn = ctk.CTkButton(root, text="Reset", command=self.reset_timer)
        self.reset_btn.pack(pady=5)
        
        # Time settings
        ctk.CTkLabel(root, text="Focus Time (min):").pack()
        self.work_entry = ctk.CTkEntry(root, textvariable=self.work_time)
        self.work_entry.pack()
        
        ctk.CTkLabel(root, text="Break Time (min):").pack()
        self.break_entry = ctk.CTkEntry(root, textvariable=self.break_time)
        self.break_entry.pack()
        
    def update_timer(self):
        total_time = self.work_time.get() * 60
        while self.running and self.time_left > 0:
            if self.paused:
                time.sleep(1)
                continue
            
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.timer_label.configure(text=f"{minutes:02}:{seconds:02}")
            self.progress.set(self.time_left / total_time)
            
            # Smooth dynamic animation
            self.animate_circle(self.time_left / total_time)
            
            time.sleep(1)
            self.time_left -= 1
        
        if self.time_left == 0:
            self.timer_label.configure(text="Time's Up!")
            self.play_alarm()
        
    def animate_circle(self, progress):
        self.canvas.delete("all")
        angle = progress * 360
        colors = ["#FF5733", "#33FF57", "#3357FF", "#F4D03F", "#8E44AD"]
        random_color = random.choice(colors)
        
        # Glowing effect with multiple overlapping arcs
        for i in range(5):
            self.canvas.create_arc(10+i, 10+i, 240-i, 240-i, start=90, extent=angle, outline=random_color, width=5-i, style=tk.ARC)
        
        self.root.update_idletasks()
    
    def play_alarm(self):
        pygame.mixer.Sound("beep.wav").play()
    
    def start_timer(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.time_left = self.work_time.get() * 60
            Thread(target=self.update_timer, daemon=True).start()
    
    def pause_timer(self):
        self.paused = not self.paused
    
    def reset_timer(self):
        self.running = False
        self.paused = False
        self.time_left = self.work_time.get() * 60
        self.timer_label.configure(text=f"{self.work_time.get()}:00")
        self.progress.set(1)
        self.canvas.delete("all")
        self.animate_circle(1)

if __name__ == "__main__":
    root = ctk.CTk()
    app = PomodoroApp(root)
    root.mainloop()
