import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import threading
import time
import re

# Set appearance and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AnimatedButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_color = self.cget("fg_color")
        self.hover_color = kwargs.get("hover_color", ("#3B8ED0", "#1F6AA5"))
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.configure(fg_color=self.hover_color, border_width=2, border_color="#FFFFFF")

    def on_leave(self, e):
        self.configure(fg_color=self.default_color, border_width=0)

class BirthdayListFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Modern headers with gradient effect
        self.headers = ["Name", "Email", "Birthday"]
        for i, header in enumerate(self.headers):
            label = ctk.CTkLabel(
                self,
                text=header,
                font=("Segoe UI", 14, "bold"),
                text_color="#FFFFFF",
                fg_color="#2B2B2B",
                corner_radius=8,
                height=40,
                anchor="center"
            )
            label.grid(row=0, column=i, padx=5, pady=(0, 10), sticky="ew")
        
        self.birthday_entries = []

    def update_birthdays(self, birthdays):
        # Clear existing entries by destroying widgets
        for entry in self.birthday_entries:
            for widget in entry:
                widget.destroy()
        self.birthday_entries.clear()

        # Add new entries
        try:
            for row, (name, email, birthday) in enumerate(birthdays, start=1):
                entry_frame = ctk.CTkFrame(self, fg_color="#3A3A3A", corner_radius=10)
                entry_frame.grid(row=row, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
                
                labels = [
                    ctk.CTkLabel(entry_frame, text=name, font=("Segoe UI", 12), anchor="w"),
                    ctk.CTkLabel(entry_frame, text=email, font=("Segoe UI", 12), anchor="w"),
                    ctk.CTkLabel(entry_frame, text=birthday, font=("Segoe UI", 12), anchor="w")
                ]
                
                for i, label in enumerate(labels):
                    label.grid(row=0, column=i, padx=10, pady=8, sticky="w")
                
                self.birthday_entries.append([entry_frame] + labels)
        except Exception as e:
            print(f"Error in update_birthdays: {e}")

class BirthdayWisherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("🎂 Birthday Wisher")
        self.geometry("900x650")
        self.configure(fg_color="#212121")

        # Database setup
        self.conn = sqlite3.connect('birthday_database.db')
        self.create_table()

        # Email configuration
        self.sender_email = None
        self.sender_password = None

        # Create UI
        self.create_ui()

        # Start birthday checking thread
        self.start_birthday_thread()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS birthdays (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                birthday DATE NOT NULL,
                custom_message TEXT
            )
        ''')
        self.conn.commit()

    def create_ui(self):
        # Main container with subtle gradient
        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#2B2B2B")
        self.main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Animated title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="🎂 Birthday Wisher",
            font=("Segoe UI", 36, "bold"),
            text_color="#FFFFFF"
        )
        self.title_label.pack(pady=(20, 30))
        self._animate_title()

        # Button frame with smooth transitions
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", pady=20, padx=20)

        button_style = {
            "corner_radius": 12,
            "font": ("Segoe UI", 16, "bold"),
            "hover_color": ("#3B8ED0", "#1F6AA5"),
            "width": 220,
            "height": 60,
            "fg_color": ("#424242", "#424242"),
            "text_color": "#FFFFFF"
        }

        buttons = [
            ("Add Birthday", self.add_birthday),
            ("View Birthdays", self.view_birthdays),
            ("Configure Email", self.configure_email)
        ]

        for text, command in buttons:
            btn = AnimatedButton(self.button_frame, text=text, command=command, **button_style)
            btn.pack(side="left", padx=15)

        # Scrollable Birthday List with modern styling
        self.birthday_list = BirthdayListFrame(
            self.main_frame,
            width=800,
            height=300,
            corner_radius=15,
            fg_color="#2B2B2B"
        )
        self.birthday_list.pack(pady=20, padx=20, fill="both", expand=True)

        # Status bar
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Ready",
            font=("Segoe UI", 12),
            text_color="#B0B0B0"
        )
        self.status_label.pack(pady=(10, 0))

        self.refresh_birthday_list()

    def _animate_title(self):
        # Simple bounce animation for title
        def bounce():
            self.title_label.configure(pady=25)
            self.after(200, lambda: self.title_label.configure(pady=30))
        self.after(2000, bounce)

    def add_birthday(self):
        name = simpledialog.askstring("Input", "Enter name:", parent=self)
        if not name:
            return
        
        email = simpledialog.askstring("Input", "Enter email:", parent=self)
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid email format")
            return
        
        birthday = simpledialog.askstring("Input", "Enter birthday (MM-DD):", parent=self)
        if not birthday or not re.match(r"\d{2}-\d{2}", birthday):
            messagebox.showerror("Error", "Invalid date format (use MM-DD)")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO birthdays (name, email, birthday) VALUES (?, ?, ?)",
                (name, email, birthday)
            )
            self.conn.commit()
            self.refresh_birthday_list()
            self.status_label.configure(text=f"Added {name}'s birthday")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add birthday: {e}")

    def view_birthdays(self):
        self.refresh_birthday_list()
        self.status_label.configure(text="Viewing all birthdays")

    def configure_email(self):
        self.sender_email = simpledialog.askstring("Input", "Enter your email:", parent=self)
        self.sender_password = simpledialog.askstring("Input", "Enter your email password:", parent=self)
        self.status_label.configure(text="Email configuration updated")

    def refresh_birthday_list(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name, email, birthday FROM birthdays")
            birthdays = cursor.fetchall()
            self.birthday_list.update_birthdays(birthdays)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh birthday list: {e}")

    def start_birthday_thread(self):
        # Placeholder for birthday checking logic
        def check_birthdays():
            while True:
                time.sleep(3600)  # Check every hour
        threading.Thread(target=check_birthdays, daemon=True).start()

def main():
    app = BirthdayWisherApp()
    app.mainloop()

if __name__ == "__main__":
    main()