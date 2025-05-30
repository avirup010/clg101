"""
Binary Calculator using Tkinter
This is a simple Binary Calculator built using Python and Tkinter. It allows users to perform 
basic arithmetic operations (addition, subtraction, multiplication, and division) on binary numbers. The results are displayed in binary format.

Features
Supports addition (+), subtraction (-), multiplication (*), and division (/).
Takes binary input and displays the result in binary format.
Uses a simple GUI built with Tkinter.
Handles invalid input and division by zero errors.
Requirements
To run this script, you need Python 3.x installed. Tkinter is included by default with Python.

Run the script:
python binary_calculator.py

Potential Improvements
Add floating-point support for division.
Enhance the UI with modern styles using ttk.
Add history tracking for previous calculations.
"""
import tkinter as tk

def binary_to_decimal(binary_str):
    return int(binary_str, 2)


def decimal_to_binary(decimal):
    return bin(decimal)[2:]


def perform_operation():
    num1 = entry_num1.get()
    num2 = entry_num2.get()
    operator = operator_var.get()

    if not all(char in '01' for char in num1) or not all(char in '01' for char in num2):
        result_label.config(text="Invalid binary input")
        return

    if operator == "+":
        result = binary_to_decimal(num1) + binary_to_decimal(num2)
    elif operator == "-":
        result = binary_to_decimal(num1) - binary_to_decimal(num2)
    elif operator == "*":
        result = binary_to_decimal(num1) * binary_to_decimal(num2)
    else:
        divisor = binary_to_decimal(num2)
        if divisor == 0:
            result_label.config(text="Division by zero is not allowed")
            return
        result = binary_to_decimal(num1) // divisor

    binary_result = decimal_to_binary(result)
    result_label.config(text="Result: " + binary_result)


# Create the main window
window = tk.Tk()
window.title("Binary Calculator")

# Create input fields
entry_num1 = tk.Entry(window, width=20)
entry_num1.grid(row=0, column=0, padx=10, pady=10)
entry_num1_label = tk.Label(window, text="Binary Number 1:")
entry_num1_label.grid(row=0, column=1)

entry_num2 = tk.Entry(window, width=20)
entry_num2.grid(row=1, column=0, padx=10, pady=10)
entry_num2_label = tk.Label(window, text="Binary Number 2:")
entry_num2_label.grid(row=1, column=1)

# Create operator selection
operator_var = tk.StringVar()
operator_var.set("+")
operator_label = tk.Label(window, text="Operator:")
operator_label.grid(row=2, column=0)
addition_radio = tk.Radiobutton(window, text="+", variable=operator_var, value="+")
addition_radio.grid(row=2, column=1)
subtraction_radio = tk.Radiobutton(window, text="-", variable=operator_var, value="-")
subtraction_radio.grid(row=2, column=2)
multiplication_radio = tk.Radiobutton(window, text="", variable=operator_var, value="")
multiplication_radio.grid(row=2, column=3)
division_radio = tk.Radiobutton(window, text="/", variable=operator_var, value="/")
division_radio.grid(row=2, column=4)

# Create result label
result_label = tk.Label(window, text="")
result_label.grid(row=3, column=0, columnspan=5)

# Create calculate button
calculate_button = tk.Button(window, text="Calculate", command=perform_operation)
calculate_button.grid(row=4, column=0, columnspan=5, pady=10)

# Start the GUI event loop
window.mainloop()
