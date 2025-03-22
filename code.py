import tkinter as tk
from tkinter import ttk
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from ttkbootstrap import Style

# Alpha Vantage API Key (Replace with your own)
API_KEY = "YOUR_API_KEY"

def fetch_stock_data():
    symbol = symbol_entry.get().upper()
    if not symbol:
        status_label.config(text="Please enter a stock symbol.", foreground="red")
        return
    
    try:
        ts = TimeSeries(key=API_KEY, output_format='pandas')
        data, meta_data = ts.get_daily(symbol=symbol, outputsize='compact')
        
        # Extract recent data
        data = data.sort_index()
        latest_close = data.iloc[-1]["4. close"]
        status_label.config(text=f"Latest Price: ${latest_close:.2f}", foreground="green")
        
        plot_stock_data(data, symbol)
    except Exception as e:
        status_label.config(text=f"Error fetching data: {e}", foreground="red")

def plot_stock_data(data, symbol):
    ax.clear()
    data['4. close'].plot(kind='line', legend=True, ax=ax, title=f"Stock Price of {symbol}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    canvas.draw()

# Initialize Tkinter UI
root = tk.Tk()
root.title("Stock Price Analyzer")
root.geometry("600x500")
style = Style("superhero")

# UI Elements
frame = ttk.Frame(root, padding=10)
frame.pack(pady=10, fill=tk.BOTH, expand=True)

ttk.Label(frame, text="Enter Stock Symbol:", font=("Arial", 12)).pack()
symbol_entry = ttk.Entry(frame, font=("Arial", 12), width=20)
symbol_entry.pack(pady=5)

fetch_button = ttk.Button(frame, text="Get Stock Data", command=fetch_stock_data)
fetch_button.pack(pady=5)

status_label = ttk.Label(frame, text="", font=("Arial", 12))
status_label.pack()

# Matplotlib Figure
fig, ax = plt.subplots(figsize=(5, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Run App
root.mainloop()
