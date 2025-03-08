import tkinter as tk
from tkinter import ttk
import requests
from datetime import datetime

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x400")
        self.root.configure(bg="#2c3e50")

        # API Key - Replace 'YOUR_API_KEY_HERE' with your actual Fixer.io API key
        self.api_key = "a2ef8843ef048b4e195640c354fd625b"

        # Style configuration
        style = ttk.Style()
        style.configure("TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 10, "bold"))
        style.configure("TCombobox", font=("Helvetica", 12))

        # Variables
        self.amount_var = tk.StringVar(value="1.0")
        self.from_currency = tk.StringVar(value="USD")
        self.to_currency = tk.StringVar(value="EUR")
        self.result_var = tk.StringVar(value="")
        self.currencies = self.fetch_currencies()

        # Main frame
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(fill="both", expand=True)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Converter tab
        self.converter_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.converter_tab, text="Converter")

        # Shortcuts tab
        self.shortcuts_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.shortcuts_tab, text="Shortcuts")

        # Setup UI
        self.setup_converter_tab()
        self.setup_shortcuts_tab()

        # Keyboard bindings
        self.root.bind("<Return>", lambda e: self.convert())
        self.root.bind("<Control-c>", lambda e: self.copy_result())
        self.root.bind("<Control-q>", lambda e: self.root.quit())

        # Animation for startup
        self.fade_in(self.main_frame)

    def fetch_currencies(self):
        try:
            url = f"http://data.fixer.io/api/latest?access_key={self.api_key}"
            response = requests.get(url)
            data = response.json()
            if data.get("success"):
                return sorted(data["rates"].keys())
            else:
                print("API error:", data.get("error"))
                return ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "INR"]
        except Exception as e:
            print(f"Error fetching currencies: {e}")
            return ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "INR"]  # Fallback

    def fetch_rates(self, base_currency):
        try:
            url = f"http://data.fixer.io/api/latest?access_key={self.api_key}&base={base_currency}"
            response = requests.get(url)
            data = response.json()
            if data.get("success"):
                return data["rates"], data["date"]
            else:
                print("API error:", data.get("error"))
                return None, None
        except Exception as e:
            print(f"Error fetching rates: {e}")
            return None, None

    def setup_converter_tab(self):
        # Amount entry
        ttk.Label(self.converter_tab, text="Amount:").grid(row=0, column=0, pady=10, padx=10, sticky="w")
        amount_entry = ttk.Entry(self.converter_tab, textvariable=self.amount_var, width=15)
        amount_entry.grid(row=0, column=1, pady=10, padx=10)

        # From currency
        ttk.Label(self.converter_tab, text="From:").grid(row=1, column=0, pady=10, padx=10, sticky="w")
        from_combo = ttk.Combobox(self.converter_tab, textvariable=self.from_currency, values=self.currencies)
        from_combo.grid(row=1, column=1, pady=10, padx=10)

        # To currency
        ttk.Label(self.converter_tab, text="To:").grid(row=2, column=0, pady=10, padx=10, sticky="w")
        to_combo = ttk.Combobox(self.converter_tab, textvariable=self.to_currency, values=self.currencies)
        to_combo.grid(row=2, column=1, pady=10, padx=10)

        # Convert button
        convert_btn = ttk.Button(self.converter_tab, text="Convert", command=self.convert)
        convert_btn.grid(row=3, column=0, columnspan=2, pady=20)

        # Result label
        self.result_label = ttk.Label(self.converter_tab, textvariable=self.result_var, font=("Helvetica", 14, "bold"))
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)

        # Last updated
        self.updated_label = ttk.Label(self.converter_tab, text="Rates last updated: Fetching...")
        self.updated_label.grid(row=5, column=0, columnspan=2, pady=10)

    def setup_shortcuts_tab(self):
        shortcuts = [
            ("Enter", "Convert currency"),
            ("Ctrl+C", "Copy result to clipboard"),
            ("Ctrl+Q", "Quit application")
        ]
        for i, (key, desc) in enumerate(shortcuts):
            ttk.Label(self.shortcuts_tab, text=f"{key}: {desc}").grid(row=i, column=0, pady=5, padx=20, sticky="w")

    def convert(self):
        try:
            amount = float(self.amount_var.get())
            from_currency = self.from_currency.get()
            to_currency = self.to_currency.get()

            rates, date = self.fetch_rates(from_currency)
            if rates:
                result = amount * rates[to_currency]
                self.result_var.set(f"{result:.2f} {to_currency}")
                self.updated_label.config(text=f"Rates last updated: {date}")
                self.animate_result()
            else:
                self.result_var.set("Error fetching rates")
        except ValueError:
            self.result_var.set("Invalid amount")
        except KeyError:
            self.result_var.set("Currency not supported")
        except Exception as e:
            self.result_var.set(f"Error: {e}")

    def copy_result(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.result_var.get())

    def fade_in(self, widget, alpha=0.0):
        alpha += 0.05
        if alpha <= 1.0:
            widget.configure(style=f"Alpha.TFrame")
            self.root.after(50, self.fade_in, widget, alpha)
        else:
            widget.configure(style="TFrame")

    def animate_result(self):
        self.result_label.configure(foreground="#e74c3c")
        self.root.after(200, lambda: self.result_label.configure(foreground="#ecf0f1"))

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
