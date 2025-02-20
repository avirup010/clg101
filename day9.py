"""Required Packages (install these first):
pip install customtkinter
pip install numpy

Program Description:
This is a modern scientific calculator with a sleek dark-themed UI and smooth animations.
It combines standard calculator functions with advanced mathematical operations.

Key Features:

Basic Operations:

Addition, subtraction, multiplication, division
Decimals and percentages


Scientific Functions:

Trigonometric (sin, cos, tan)
Logarithms (ln, log)
Powers and roots (x², √, xʸ)
Constants (π, e)
Factorial


UI Features:

Dark mode interface
Animated calculations
RAD/DEG mode switch
Color-coded buttons for different operations


How to Run:

Save the code in a .py file
Make sure you have Python 3.x installed
Install the required packages using pip
Run the file using Python

System Requirements:

Python 3.x
Windows/Mac/Linux operating system
Basic graphics support for tkinter"""

import customtkinter as ctk
import math
from decimal import Decimal, getcontext
import time
import threading
import numpy as np

class AnimatedLabel(ctk.CTkLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_value = 0
        self._target_value = 0
        
    def animate_to(self, value, duration=0.5):
        self._target_value = value
        start_time = time.time()
        
        def animation():
            while time.time() - start_time < duration:
                progress = (time.time() - start_time) / duration
                eased_progress = 1 - (1 - progress) * (1 - progress)
                current = self._current_value + (self._target_value - self._current_value) * eased_progress
                self.configure(text=f"{current:.6f}")
                time.sleep(0.016)
            self.configure(text=f"{self._target_value:.6f}")
            self._current_value = self._target_value
            
        threading.Thread(target=animation, daemon=True).start()

class ModernCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Advanced Scientific Calculator")
        self.geometry("800x600")
        self.configure(fg_color="#1a1a1a")
        
        # Configure grid
        self.grid_columnconfigure((0,1,2,3,4,5,6,7), weight=1)
        
        # Initialize calculator state
        self.current_number = ""
        self.stored_number = None
        self.current_operation = None
        self.is_radian = True
        getcontext().prec = 10
        
        # Define colors
        self.default_button_color = "#1f1f1f"
        self.default_hover_color = "#2d2d2d"
        self.function_color = "#007AFF"
        self.operation_color = "#ff9500"
        self.special_color = "#ff3b30"
        
        # Create display
        self.result_var = AnimatedLabel(
            self,
            text="0",
            font=("Helvetica", 40),
            text_color="#ffffff"
        )
        self.result_var.grid(row=0, column=0, columnspan=8, pady=(20,40), sticky="e", padx=20)
        
        # Create mode switch
        self.mode_switch = ctk.CTkSwitch(
            self,
            text="RAD/DEG",
            command=self.toggle_mode,
            fg_color=self.function_color,
            button_color=self.operation_color,
            button_hover_color=self.operation_color
        )
        self.mode_switch.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        
        self.create_buttons()
    
    def create_buttons(self):
        # Scientific functions
        scientific_buttons = [
            ("sin", 2, 0), ("cos", 2, 1), ("tan", 2, 2),
            ("ln", 3, 0), ("log", 3, 1), ("√", 3, 2),
            ("x²", 4, 0), ("xʸ", 4, 1), ("1/x", 4, 2),
            ("π", 5, 0), ("e", 5, 1), ("!", 5, 2),
        ]
        
        # Basic operations
        basic_buttons = [
            ("C", 2, 3, self.special_color), ("(", 2, 4), (")", 2, 5), ("÷", 2, 6, self.operation_color),
            ("7", 3, 3), ("8", 3, 4), ("9", 3, 5), ("×", 3, 6, self.operation_color),
            ("4", 4, 3), ("5", 4, 4), ("6", 4, 5), ("−", 4, 6, self.operation_color),
            ("1", 5, 3), ("2", 5, 4), ("3", 5, 5), ("+", 5, 6, self.operation_color),
            ("0", 6, 3, None, 2), (".", 6, 5), ("=", 6, 6, self.operation_color)
        ]
        
        # Create all buttons
        for button in scientific_buttons + basic_buttons:
            text = button[0]
            row = button[1]
            col = button[2]
            color = button[3] if len(button) > 3 else self.function_color if button in scientific_buttons else self.default_button_color
            colspan = button[4] if len(button) > 4 else 1
            
            btn = ctk.CTkButton(
                self,
                text=text,
                width=70,
                height=70,
                corner_radius=35,
                fg_color=color,
                text_color="#ffffff",
                font=("Helvetica", 20),
                hover_color=self.default_hover_color if color == self.default_button_color else color,
                command=lambda t=text: self.button_click(t)
            )
            btn.grid(row=row, column=col, columnspan=colspan, padx=3, pady=3, sticky="nsew")
    
    def toggle_mode(self):
        self.is_radian = not self.is_radian
    
    def calculate_scientific(self, function, value):
        try:
            num = float(value)
            if function == "sin":
                if not self.is_radian:
                    num = math.radians(num)
                return math.sin(num)
            elif function == "cos":
                if not self.is_radian:
                    num = math.radians(num)
                return math.cos(num)
            elif function == "tan":
                if not self.is_radian:
                    num = math.radians(num)
                return math.tan(num)
            elif function == "ln":
                return math.log(num)
            elif function == "log":
                return math.log10(num)
            elif function == "√":
                return math.sqrt(num)
            elif function == "x²":
                return num ** 2
            elif function == "1/x":
                return 1 / num
            elif function == "!":
                return math.factorial(int(num))
        except Exception:
            return "Error"
    
    def button_click(self, value):
        if value in ["sin", "cos", "tan", "ln", "log", "√", "x²", "1/x", "!"]:
            current = float(self.current_number or self.result_var.cget("text"))
            result = self.calculate_scientific(value, current)
            if result == "Error":
                self.result_var.configure(text="Error")
            else:
                self.result_var.animate_to(result)
            self.current_number = ""
            
        elif value == "π":
            self.current_number = str(math.pi)
            self.result_var.animate_to(math.pi)
            
        elif value == "e":
            self.current_number = str(math.e)
            self.result_var.animate_to(math.e)
            
        elif value == "xʸ":
            if self.stored_number and self.current_number:
                base = float(self.stored_number)
                exponent = float(self.current_number)
                result = base ** exponent
                self.result_var.animate_to(result)
                self.current_number = ""
                self.stored_number = None
            else:
                self.stored_number = float(self.current_number or self.result_var.cget("text"))
                self.current_number = ""
                self.current_operation = "xʸ"
            
        elif value.isdigit() or value == ".":
            if self.current_operation and not self.current_number:
                self.result_var.configure(text="0")
            if value == "." and "." in self.current_number:
                return
            self.current_number += value
            self.result_var.configure(text=self.current_number)
            
        elif value in ("+", "−", "×", "÷"):
            if self.stored_number and self.current_number:
                self.calculate()
            self.stored_number = float(self.current_number or self.result_var.cget("text"))
            self.current_operation = value
            self.current_number = ""
            
        elif value == "=":
            self.calculate()
            
        elif value == "C":
            self.clear()
    
    def calculate(self):
        if not self.stored_number or (not self.current_operation and self.current_operation != "xʸ"):
            return
            
        current = float(self.current_number or self.result_var.cget("text"))
        operations = {
            "+": lambda x, y: x + y,
            "−": lambda x, y: x - y,
            "×": lambda x, y: x * y,
            "÷": lambda x, y: x / y if y != 0 else "Error",
            "xʸ": lambda x, y: x ** y
        }
        
        try:
            result = operations[self.current_operation](self.stored_number, current)
            if result == "Error":
                self.result_var.configure(text="Error")
            else:
                self.result_var.animate_to(result)
            self.stored_number = None
            self.current_operation = None
            self.current_number = ""
        except Exception:
            self.result_var.configure(text="Error")
            self.clear()
    
    def clear(self):
        self.current_number = ""
        self.stored_number = None
        self.current_operation = None
        self.result_var.animate_to(0)

if __name__ == "__main__":
    app = ModernCalculator()
    app.mainloop()