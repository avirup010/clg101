'''
Personal Finance Tracker using Tkinter and Matplotlib
Tracks income and expenses categorized as Need, Want, and Fun
Visual representation using a pie chart
Data is stored persistently in finance_data.json
Modern UI with rounded corners for a clean look
Footer positioned at the bottom-right corner in a styled box
Dependencies: tkinter, matplotlib, json (built-in)
Run the script using:
python expense_tracker.py
'''


import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

# Data storage
DATA_FILE = "finance_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"income": 0, "expenses": {"Need": 0, "Want": 0, "Fun": 0}}

def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(finance_data, file)

def add_income():
    try:
        amount = float(income_entry.get())
        finance_data["income"] += amount
        save_data()
        update_display()
    except ValueError:
        messagebox.showerror("Error", "Invalid amount")
    income_entry.delete(0, tk.END)

def add_expense():
    try:
        amount = float(expense_entry.get())
        category = category_var.get()
        finance_data["expenses"][category] += amount
        save_data()
        update_display()
    except ValueError:
        messagebox.showerror("Error", "Invalid amount")
    expense_entry.delete(0, tk.END)

def update_display():
    income_label.config(text=f"Income: ₹{finance_data['income']:.2f}")
    for cat, lbl in expense_labels.items():
        lbl.config(text=f"{cat}: ₹{finance_data['expenses'][cat]:.2f}")
    update_chart()

def update_chart():
    ax.clear()
    categories = list(finance_data["expenses"].keys())
    values = list(finance_data["expenses"].values())
    
    # Prevent division errors
    if sum(values) == 0:
        values = [1] * len(categories)
    
    ax.pie(values, labels=categories, autopct='%1.1f%%', colors=["#E74C3C", "#F39C12", "#2ECC71"],
           startangle=90, wedgeprops={"edgecolor": "black"})
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)
    canvas.draw()

# Load data
finance_data = load_data()

# UI Setup
root = tk.Tk()
root.title("Personal Finance Tracker")
root.geometry("500x600")
root.configure(bg="#2C3E50")
root.option_add('*TButton*Padding', 10)

# Header
tk.Label(root, text="Finance Tracker", font=("Teko", 24), bg="#2C3E50", fg="#ECF0F1").pack(pady=10)

# Income Section
income_frame = tk.Frame(root, bg="#2C3E50")
income_frame.pack(pady=5)
tk.Label(income_frame, text="Add Income:", font=("IBM Plex Mono", 14), bg="#2C3E50", fg="#BDC3C7").pack()
income_entry = tk.Entry(income_frame, font=("IBM Plex Mono", 14))
income_entry.pack(pady=5)
tk.Button(income_frame, text="Add", font=("IBM Plex Mono", 12), command=add_income, bg="#3498DB", fg="#ffffff").pack()

# Expense Section
expense_frame = tk.Frame(root, bg="#2C3E50")
expense_frame.pack(pady=5)
tk.Label(expense_frame, text="Add Expense:", font=("IBM Plex Mono", 14), bg="#2C3E50", fg="#BDC3C7").pack()
expense_entry = tk.Entry(expense_frame, font=("IBM Plex Mono", 14))
expense_entry.pack(pady=5)
category_var = tk.StringVar(value="Need")
category_menu = ttk.Combobox(expense_frame, textvariable=category_var, values=["Need", "Want", "Fun"], state="readonly")
category_menu.pack(pady=5)
tk.Button(expense_frame, text="Add", font=("IBM Plex Mono", 12), command=add_expense, bg="#E74C3C", fg="#ffffff").pack()

# Display Section
summary_frame = tk.Frame(root, bg="#34495E", bd=2)
summary_frame.pack(pady=10, fill=tk.X, padx=20)
income_label = tk.Label(summary_frame, font=("IBM Plex Mono", 14), bg="#34495E", fg="#2ECC71")
income_label.pack(pady=5)
expense_labels = {cat: tk.Label(summary_frame, font=("IBM Plex Mono", 14), bg="#34495E", fg="#F1C40F") for cat in finance_data["expenses"]}
for lbl in expense_labels.values():
    lbl.pack()

# Chart Section
fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Footer
footer_frame = tk.Frame(root, bg="#000000", bd=2, relief="ridge")
footer_frame.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)
footer = tk.Label(footer_frame, text="Developed by Avi", font=("IBM Plex Mono", 12), bg="#000000", fg="#ffffff", padx=10, pady=5)
footer.pack()

update_display()
root.mainloop()
