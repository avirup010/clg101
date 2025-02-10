import tkinter as tk
from tkinter import ttk
from tkinter import font

# Conversion formulas
def convert():
    try:
        value = float(entry_value.get())
        from_unit_value = from_unit.get()
        to_unit_value = to_unit.get()
        category = category_var.get()
        
        conversion_factors = {
            "Length": {
                "Meter": 1, "Kilometer": 0.001, "Centimeter": 100, "Millimeter": 1000, 
                "Inch": 39.3701, "Foot": 3.28084, "Yard": 1.09361, "Mile": 0.000621371
            },
            "Weight": {
                "Kilogram": 1, "Gram": 1000, "Pound": 2.20462, "Ounce": 35.274, "Ton": 0.001
            },
            "Temperature": {
                "Celsius": lambda x: x, "Fahrenheit": lambda x: (x * 9/5) + 32, "Kelvin": lambda x: x + 273.15
            },
            "Time": {
                "Second": 1, "Minute": 1/60, "Hour": 1/3600, "Day": 1/86400
            },
            "Volume": {
                "Liter": 1, "Milliliter": 1000, "Cubic Meter": 0.001, "Gallon": 0.264172, "Pint": 2.11338
            }
        }

        if category == "Temperature":
            if from_unit_value == "Celsius" and to_unit_value == "Fahrenheit":
                converted_value = (value * 9/5) + 32
            elif from_unit_value == "Celsius" and to_unit_value == "Kelvin":
                converted_value = value + 273.15
            elif from_unit_value == "Fahrenheit" and to_unit_value == "Celsius":
                converted_value = (value - 32) * 5/9
            elif from_unit_value == "Fahrenheit" and to_unit_value == "Kelvin":
                converted_value = (value - 32) * 5/9 + 273.15
            elif from_unit_value == "Kelvin" and to_unit_value == "Celsius":
                converted_value = value - 273.15
            elif from_unit_value == "Kelvin" and to_unit_value == "Fahrenheit":
                converted_value = (value - 273.15) * 9/5 + 32
            else:
                converted_value = value
        else:
            converted_value = value * (conversion_factors[category][to_unit_value] / conversion_factors[category][from_unit_value])
        
        result.set(f"{converted_value:.4f} {to_unit_value}")
    except ValueError:
        result.set("Invalid Input")

# Function to update units based on category
def update_units(*args):
    category = category_var.get()
    units = unit_options.get(category, [])
    from_unit_menu['values'] = units
    to_unit_menu['values'] = units
    from_unit.set(units[0])
    to_unit.set(units[1] if len(units) > 1 else units[0])

def resize(event):
    container_frame.config(width=root.winfo_width(), height=root.winfo_height())

def animate(event):
    entry_value.config(bg="#D5F5E3")
    root.after(300, lambda: entry_value.config(bg="#FFFFFF"))

root = tk.Tk()
root.title("Advanced Unit Converter")
root.geometry("800x600")
root.minsize(600, 400)
root.configure(bg="#1E1E1E")
root.bind("<Configure>", resize)

# Define categories and units
unit_options = {
    "Length": ["Meter", "Kilometer", "Centimeter", "Millimeter", "Inch", "Foot", "Yard", "Mile"],
    "Weight": ["Kilogram", "Gram", "Pound", "Ounce", "Ton"],
    "Temperature": ["Celsius", "Fahrenheit", "Kelvin"],
    "Time": ["Second", "Minute", "Hour", "Day"],
    "Volume": ["Liter", "Milliliter", "Cubic Meter", "Gallon", "Pint"],
}

category_var = tk.StringVar(value="Length")
from_unit = tk.StringVar(value="Meter")
to_unit = tk.StringVar(value="Kilometer")
result = tk.StringVar()

container_frame = tk.Frame(root, bg="#2C3E50", padx=20, pady=20)
container_frame.pack(fill=tk.BOTH, expand=True)

header = tk.Label(container_frame, text="Unit Converter", font=("Segoe UI", 24, "bold"), bg="#2C3E50", fg="#ECF0F1")
header.pack(pady=10)

category_menu = ttk.Combobox(container_frame, textvariable=category_var, values=list(unit_options.keys()), state="readonly")
category_menu.pack(fill=tk.X, padx=10, pady=5)
category_menu.bind("<<ComboboxSelected>>", update_units)

entry_value = tk.Entry(container_frame, font=("Segoe UI", 16), width=10, relief="flat", bg="#FFFFFF")
entry_value.pack(pady=5)
entry_value.bind("<KeyRelease>", animate)

from_unit_menu = ttk.Combobox(container_frame, textvariable=from_unit, values=unit_options["Length"], state="readonly")
from_unit_menu.pack(fill=tk.X, padx=10, pady=5)

to_unit_menu = ttk.Combobox(container_frame, textvariable=to_unit, values=unit_options["Length"], state="readonly")
to_unit_menu.pack(fill=tk.X, padx=10, pady=5)

convert_button = tk.Button(container_frame, text="Convert", font=("Segoe UI", 16, "bold"), bg="#3498DB", fg="#ffffff", relief="flat", command=convert)
convert_button.pack(pady=10)

result_label = tk.Label(container_frame, textvariable=result, font=("Segoe UI", 18, "bold"), bg="#2C3E50", fg="#E74C3C")
result_label.pack(pady=10)


root.mainloop()
