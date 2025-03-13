import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import time
import threading
import math

# Set theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class BMICalculator:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("BMI Calculator")
        self.app.geometry("500x700")
        self.app.resizable(False, False)
        
        # Variables
        self.height_var = ctk.DoubleVar(value=170)
        self.weight_var = ctk.DoubleVar(value=70)
        self.bmi_value = ctk.DoubleVar(value=0)
        self.bmi_category = ctk.StringVar(value="")
        self.animation_in_progress = False
        
        # Setup UI
        self.setup_ui()
        
        # Calculate initial BMI
        self.calculate_bmi()
        
    def setup_ui(self):
        # Main container with padding
        main_frame = ctk.CTkFrame(self.app, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="BMI Calculator", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(0, 30))
        
        # Height input section
        height_frame = ctk.CTkFrame(main_frame)
        height_frame.pack(fill="x", pady=10)
        
        height_label = ctk.CTkLabel(
            height_frame, 
            text="Height (cm):", 
            font=ctk.CTkFont(size=16)
        )
        height_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        height_slider = ctk.CTkSlider(
            height_frame,
            from_=100,
            to=220,
            number_of_steps=120,
            variable=self.height_var,
            command=self.on_slider_change
        )
        height_slider.pack(fill="x", padx=10, pady=5)
        
        self.height_value_label = ctk.CTkLabel(
            height_frame,
            text=f"{int(self.height_var.get())} cm",
            font=ctk.CTkFont(size=16)
        )
        self.height_value_label.pack(anchor="e", padx=10, pady=(5, 10))
        
        # Weight input section
        weight_frame = ctk.CTkFrame(main_frame)
        weight_frame.pack(fill="x", pady=10)
        
        weight_label = ctk.CTkLabel(
            weight_frame, 
            text="Weight (kg):", 
            font=ctk.CTkFont(size=16)
        )
        weight_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        weight_slider = ctk.CTkSlider(
            weight_frame,
            from_=30,
            to=150,
            number_of_steps=120,
            variable=self.weight_var,
            command=self.on_slider_change
        )
        weight_slider.pack(fill="x", padx=10, pady=5)
        
        self.weight_value_label = ctk.CTkLabel(
            weight_frame,
            text=f"{int(self.weight_var.get())} kg",
            font=ctk.CTkFont(size=16)
        )
        self.weight_value_label.pack(anchor="e", padx=10, pady=(5, 10))
        
        # Calculate button
        calculate_button = ctk.CTkButton(
            main_frame, 
            text="Calculate BMI", 
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.animate_calculation,
            height=40
        )
        calculate_button.pack(pady=20)
        
        # Results section
        result_frame = ctk.CTkFrame(main_frame)
        result_frame.pack(fill="x", pady=10)
        
        # BMI result display
        self.bmi_display = ctk.CTkLabel(
            result_frame,
            text="0.0",
            font=ctk.CTkFont(size=50, weight="bold")
        )
        self.bmi_display.pack(pady=(20, 10))
        
        self.category_label = ctk.CTkLabel(
            result_frame,
            text="",
            font=ctk.CTkFont(size=18)
        )
        self.category_label.pack(pady=(0, 20))
        
        # Progress bar for BMI visualization
        self.bmi_progress_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
        self.bmi_progress_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.progress_bar = ttk.Progressbar(
            self.bmi_progress_frame, 
            orient="horizontal", 
            length=100, 
            mode="determinate"
        )
        self.progress_bar.pack(fill="x")
        
        # BMI scale labels
        scale_frame = ctk.CTkFrame(self.bmi_progress_frame, fg_color="transparent")
        scale_frame.pack(fill="x", pady=(5, 0))
        
        underweight = ctk.CTkLabel(scale_frame, text="Underweight", font=("Arial", 10))
        underweight.pack(side="left")
        
        normal = ctk.CTkLabel(scale_frame, text="Normal", font=("Arial", 10))
        normal.pack(side="left", padx=(30, 30))
        
        overweight = ctk.CTkLabel(scale_frame, text="Overweight", font=("Arial", 10))
        overweight.pack(side="left")
        
        obese = ctk.CTkLabel(scale_frame, text="Obese", font=("Arial", 10))
        obese.pack(side="right")
        
        # Information section
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(30, 0))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="BMI Categories:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        info_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        categories = [
            "• Underweight: BMI less than 18.5",
            "• Normal weight: BMI 18.5-24.9",
            "• Overweight: BMI 25-29.9",
            "• Obesity: BMI 30 or greater"
        ]
        
        for category in categories:
            cat_label = ctk.CTkLabel(
                info_frame,
                text=category,
                font=ctk.CTkFont(size=14),
                anchor="w"
            )
            cat_label.pack(anchor="w", padx=20, pady=2)
            
        disclaimer = ctk.CTkLabel(
            info_frame,
            text="BMI is a screening tool and not a diagnostic of\nbody fatness or health.",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        disclaimer.pack(anchor="w", padx=10, pady=(10, 10))
        
    def on_slider_change(self, event=None):
        self.height_value_label.configure(text=f"{int(self.height_var.get())} cm")
        self.weight_value_label.configure(text=f"{int(self.weight_var.get())} kg")
    
    def calculate_bmi(self):
        height_m = self.height_var.get() / 100  # Convert cm to m
        weight_kg = self.weight_var.get()
        
        if height_m > 0:
            bmi = weight_kg / (height_m * height_m)
            self.bmi_value.set(bmi)
            
            # Update progress bar based on BMI (0-40 scale)
            progress_value = min(100, (bmi / 40) * 100)
            self.progress_bar["value"] = progress_value
            
            # Determine BMI category
            if bmi < 18.5:
                category = "Underweight"
                color = "#3498db"  # Blue
            elif 18.5 <= bmi < 25:
                category = "Normal weight"
                color = "#2ecc71"  # Green
            elif 25 <= bmi < 30:
                category = "Overweight"
                color = "#f39c12"  # Orange
            else:
                category = "Obese"
                color = "#e74c3c"  # Red
            
            self.bmi_category.set(category)
            self.category_label.configure(text=category, text_color=color)
            self.update_bmi_display(bmi)
    
    def update_bmi_display(self, bmi):
        self.bmi_display.configure(text=f"{bmi:.1f}")
    
    def animate_calculation(self):
        if not self.animation_in_progress:
            self.animation_in_progress = True
            threading.Thread(target=self._run_animation, daemon=True).start()
    
    def _run_animation(self):
        # Store current values
        start_value = float(self.bmi_display.cget("text"))
        end_value = self.height_var.get() > 0 and (self.weight_var.get() / ((self.height_var.get() / 100) ** 2)) or 0
        
        # Reset text color for animation
        self.bmi_display.configure(text_color=("black", "white"))
        
        # Animate counting up/down
        duration = 1.0  # seconds
        steps = 30
        step_time = duration / steps
        
        for i in range(steps + 1):
            t = i / steps
            # Ease in-out function
            factor = -math.cos(t * math.pi) / 2 + 0.5
            current = start_value + (end_value - start_value) * factor
            
            # Update UI in main thread
            self.app.after(0, lambda val=current: self.bmi_display.configure(text=f"{val:.1f}"))
            time.sleep(step_time)
        
        # Final calculation and update
        self.app.after(0, self.calculate_bmi)
        self.animation_in_progress = False
        
    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = BMICalculator()
    app.run()