import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import time
import json
import os
from plyer import notification
import threading

class ClassSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Class Scheduler")
        self.root.geometry("700x500")
        self.root.configure(bg="#1a1a1a")  # Dark theme background

        self.classes = self.load_classes()
        self.notification_thread = None
        self.running = True

        self.create_ui()
        self.start_notification_checker()

    def create_ui(self):
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Helvetica", 10, "bold"), padding=8, background="#3d3d3d", 
                       foreground="white", borderwidth=0)
        style.map("TButton", background=[("active", "#5a5a5a")])
        style.configure("Accent.TButton", background="#007bff", foreground="white")
        style.map("Accent.TButton", background=[("active", "#0056b3")])

        # Header
        header_frame = tk.Frame(self.root, bg="#252526")
        header_frame.pack(fill="x", pady=(0, 10))
        tk.Label(header_frame, text="Class Scheduler", font=("Helvetica", 18, "bold"), 
                bg="#252526", fg="#ffffff").pack(pady=15)

        # Main container
        main_container = tk.Frame(self.root, bg="#1a1a1a")
        main_container.pack(pady=20, padx=20, fill="both", expand=True)

        # Add class section
        add_frame = tk.Frame(main_container, bg="#252526", bd=0)
        add_frame.pack(fill="x", pady=(0, 20))

        # Input fields with modern styling
        self.class_name = tk.Entry(add_frame, font=("Helvetica", 11), bg="#3d3d3d", 
                                 fg="white", insertbackground="white", bd=0)
        self.class_name.insert(0, "Class Name")
        self.class_name.bind("<FocusIn>", lambda e: self.clear_placeholder(self.class_name, "Class Name"))
        self.class_name.pack(side="left", padx=5, pady=10, ipady=5)

        self.class_time = tk.Entry(add_frame, font=("Helvetica", 11), bg="#3d3d3d", 
                                 fg="white", insertbackground="white", bd=0, width=10)
        self.class_time.insert(0, "HH:MM")
        self.class_time.bind("<FocusIn>", lambda e: self.clear_placeholder(self.class_time, "HH:MM"))
        self.class_time.pack(side="left", padx=5, pady=10, ipady=5)

        self.class_days = tk.Entry(add_frame, font=("Helvetica", 11), bg="#3d3d3d", 
                                 fg="white", insertbackground="white", bd=0, width=15)
        self.class_days.insert(0, "M,T,W,Th,F")
        self.class_days.bind("<FocusIn>", lambda e: self.clear_placeholder(self.class_days, "M,T,W,Th,F"))
        self.class_days.pack(side="left", padx=5, pady=10, ipady=5)

        ttk.Button(add_frame, text="Add", style="Accent.TButton", 
                  command=self.add_class).pack(side="left", padx=5)

        # Schedule display
        self.schedule_canvas = tk.Canvas(main_container, bg="#1a1a1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.schedule_canvas.yview)
        self.scrollable_frame = tk.Frame(self.schedule_canvas, bg="#1a1a1a")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.schedule_canvas.configure(scrollregion=self.schedule_canvas.bbox("all"))
        )

        self.schedule_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.schedule_canvas.configure(yscrollcommand=scrollbar.set)

        self.schedule_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.update_schedule_display()

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    def load_classes(self):
        try:
            with open("classes.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_classes(self):
        with open("classes.json", "w") as f:
            json.dump(self.classes, f)

    def add_class(self):
        name = self.class_name.get().strip()
        time_str = self.class_time.get().strip()
        days = self.class_days.get().strip().upper().split(",")

        if not all([name, time_str, days]) or name == "Class Name" or time_str == "HH:MM":
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM (24-hour)")
            return

        valid_days = {"M", "T", "W", "TH", "F"}
        if not all(day in valid_days for day in days):
            messagebox.showerror("Error", "Invalid days. Use M,T,W,Th,F")
            return

        self.classes.append({"name": name, "time": time_str, "days": days})
        self.save_classes()
        self.update_schedule_display()
        
        # Reset fields with animation
        self.fade_entry(self.class_name, "Class Name")
        self.fade_entry(self.class_time, "HH:MM")
        self.fade_entry(self.class_days, "M,T,W,Th,F")

    def fade_entry(self, entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)
        entry.config(fg="#808080")

    def update_schedule_display(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for i, class_info in enumerate(self.classes):
            class_frame = tk.Frame(self.scrollable_frame, bg="#252526", bd=0)
            class_frame.pack(fill="x", pady=5, padx=5)
            
            # Card animation
            class_frame.place(relx=1.0, rely=(i * 0.1), anchor="ne")
            class_frame.after(100 + (i * 100), lambda f=class_frame: self.animate_card(f))

            # Class info
            tk.Label(class_frame, text=f"{class_info['name']}", font=("Helvetica", 12, "bold"), 
                    bg="#252526", fg="#ffffff").pack(side="left", padx=15, pady=10)
            tk.Label(class_frame, text=f"{class_info['time']} - {', '.join(class_info['days'])}", 
                    bg="#252526", fg="#b0b0b0").pack(side="left", padx=15, pady=10)
            
            delete_btn = ttk.Button(class_frame, text="Delete", 
                                  command=lambda idx=i: self.delete_class(idx))
            delete_btn.pack(side="right", padx=10, pady=5)
            delete_btn.configure(style="TButton")

    def animate_card(self, frame):
        def move_frame(x):
            if x > 0:
                frame.place(relx=x/100, rely=frame.winfo_y()/self.scrollable_frame.winfo_height())
                frame.after(10, lambda: move_frame(x-5))
            else:
                frame.place(relx=0, rely=frame.winfo_y()/self.scrollable_frame.winfo_height())
        
        move_frame(100)

    def delete_class(self, index):
        self.classes.pop(index)
        self.save_classes()
        self.update_schedule_display()

    def check_notifications(self):
        while self.running:
            current_time = datetime.now()
            current_day = current_time.strftime("%A")[0:2].upper()

            for class_info in self.classes:
                class_time = datetime.strptime(class_info["time"], "%H:%M")
                class_datetime = datetime.now().replace(hour=class_time.hour, 
                                                      minute=class_time.minute, 
                                                      second=0, microsecond=0)
                
                time_diff = (class_datetime - current_time).total_seconds() / 60
                
                if current_day in class_info["days"] and 4.5 <= time_diff <= 5.5:
                    notification.notify(
                        title="Class Reminder",
                        message=f"{class_info['name']} starts in 5 minutes!",
                        timeout=10
                    )

            time.sleep(60)

    def start_notification_checker(self):
        self.notification_thread = threading.Thread(target=self.check_notifications, daemon=True)
        self.notification_thread.start()

    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClassSchedulerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()