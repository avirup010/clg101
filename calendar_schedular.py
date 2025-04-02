import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import calendar
import json
import os
from ttkthemes import ThemedTk

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calendar Scheduler")
        self.root.geometry("1200x800")
        
        # Set dark mode colors
        self.bg_color = "#36393F"  # Discord dark background
        self.sidebar_color = "#2F3136"  # Discord sidebar
        self.text_color = "#FFFFFF"  # White text
        self.accent_color = "#7289DA"  # Discord blurple
        self.secondary_color = "#40444B"  # Discord input background
        
        # Configure the root window
        self.root.configure(bg=self.bg_color)
        
        # Initialize data structure
        self.events = self.load_events()
        self.selected_date = datetime.date.today()
        
        # Create main layout
        self.create_layout()
        
        # Initially load today's events
        self.display_events_for_date(self.selected_date)

    def create_layout(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create sidebar
        self.create_sidebar(main_frame)
        
        # Create calendar widget
        self.create_calendar_widget(main_frame)
        
        # Create events display area
        self.create_events_area(main_frame)
        
        # Create input area
        self.create_input_area(main_frame)

    def create_sidebar(self, parent):
        # Sidebar frame
        sidebar = tk.Frame(parent, width=200, bg=self.sidebar_color)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # App title/logo
        logo_frame = tk.Frame(sidebar, bg=self.sidebar_color)
        logo_frame.pack(fill=tk.X, pady=(20, 30))
        
        logo_label = tk.Label(logo_frame, text="📅 Scheduler", font=("Arial", 18, "bold"), 
                              bg=self.sidebar_color, fg=self.text_color)
        logo_label.pack()
        
        # Navigation buttons
        buttons_data = [
            ("Today", self.go_to_today),
            ("This Week", self.view_this_week),
            ("This Month", self.view_this_month),
            ("Add Event", self.focus_add_event)
        ]
        
        for text, command in buttons_data:
            btn = tk.Button(sidebar, text=text, font=("Arial", 12), 
                         bg=self.secondary_color, fg=self.text_color,
                         activebackground=self.accent_color, activeforeground=self.text_color,
                         relief=tk.FLAT, command=command, cursor="hand2")
            btn.pack(fill=tk.X, pady=5, ipady=5, padx=10)

    def create_calendar_widget(self, parent):
        # Calendar frame
        cal_frame = tk.Frame(parent, bg=self.bg_color)
        cal_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Month navigation
        nav_frame = tk.Frame(cal_frame, bg=self.bg_color)
        nav_frame.pack(fill=tk.X)
        
        prev_btn = tk.Button(nav_frame, text="◀", font=("Arial", 12), 
                          bg=self.secondary_color, fg=self.text_color,
                          activebackground=self.accent_color, relief=tk.FLAT,
                          command=self.prev_month, cursor="hand2")
        prev_btn.pack(side=tk.LEFT, padx=5)
        
        # Current month/year display
        self.month_label = tk.Label(nav_frame, text=self.get_month_year_str(), 
                                   font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.text_color)
        self.month_label.pack(side=tk.LEFT, expand=True)
        
        next_btn = tk.Button(nav_frame, text="▶", font=("Arial", 12), 
                          bg=self.secondary_color, fg=self.text_color,
                          activebackground=self.accent_color, relief=tk.FLAT,
                          command=self.next_month, cursor="hand2")
        next_btn.pack(side=tk.RIGHT, padx=5)
        
        # Calendar days grid
        cal_grid = tk.Frame(cal_frame, bg=self.bg_color)
        cal_grid.pack(fill=tk.X, pady=10)
        
        # Weekday headers
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(weekdays):
            lbl = tk.Label(cal_grid, text=day, width=4, font=("Arial", 10),
                         bg=self.bg_color, fg=self.text_color)
            lbl.grid(row=0, column=i, pady=(0, 5))
        
        # Create calendar buttons
        self.cal_buttons = []
        for row in range(6):
            for col in range(7):
                btn = tk.Button(cal_grid, text="", width=4, height=2,
                             bg=self.secondary_color, activebackground=self.accent_color,
                             fg=self.text_color, relief=tk.FLAT, cursor="hand2")
                btn.grid(row=row+1, column=col, padx=2, pady=2, sticky="nsew")
                self.cal_buttons.append(btn)
        
        # Fill calendar with days
        self.update_calendar()

    def create_events_area(self, parent):
        # Create events display area
        events_frame = tk.Frame(parent, bg=self.bg_color)
        events_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Date header
        date_frame = tk.Frame(events_frame, bg=self.bg_color)
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.date_label = tk.Label(date_frame, text=self.format_date(self.selected_date), 
                                 font=("Arial", 16, "bold"), bg=self.bg_color, fg=self.text_color)
        self.date_label.pack(side=tk.LEFT)
        
        # Events list
        events_list_frame = tk.Frame(events_frame, bg=self.secondary_color, bd=1)
        events_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(events_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Events listbox
        self.events_list = tk.Listbox(events_list_frame, bg=self.secondary_color, 
                                    fg=self.text_color, font=("Arial", 11),
                                    bd=0, highlightthickness=0, 
                                    selectbackground=self.accent_color,
                                    selectforeground=self.text_color,
                                    activestyle="none")
        self.events_list.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        self.events_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.events_list.yview)
        
        # Bind events
        self.events_list.bind("<Double-1>", self.edit_event)
        self.events_list.bind("<Delete>", self.delete_selected_event)

    def create_input_area(self, parent):
        # Input frame
        input_frame = tk.Frame(parent, bg=self.bg_color)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Time input
        time_frame = tk.Frame(input_frame, bg=self.bg_color)
        time_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(time_frame, text="Time:", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=(0, 5))
        
        # Hour and minute selection
        self.hour_var = tk.StringVar(value="12")
        hour_spinner = ttk.Spinbox(time_frame, from_=0, to=23, width=3, 
                                 textvariable=self.hour_var, wrap=True)
        hour_spinner.pack(side=tk.LEFT)
        
        tk.Label(time_frame, text=":", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)
        
        self.minute_var = tk.StringVar(value="00")
        minute_spinner = ttk.Spinbox(time_frame, from_=0, to=59, width=3, 
                                   textvariable=self.minute_var, wrap=True,
                                   format="%02.0f")
        minute_spinner.pack(side=tk.LEFT)
        
        # Duration
        tk.Label(time_frame, text="Duration (min):", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=(15, 5))
        
        self.duration_var = tk.StringVar(value="60")
        duration_spinner = ttk.Spinbox(time_frame, from_=5, to=480, width=4, 
                                     textvariable=self.duration_var, increment=5)
        duration_spinner.pack(side=tk.LEFT)
        
        # Event input
        event_frame = tk.Frame(input_frame, bg=self.bg_color)
        event_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Event name entry
        self.event_entry = tk.Entry(event_frame, bg=self.secondary_color, fg=self.text_color,
                                  insertbackground=self.text_color, font=("Arial", 12),
                                  relief=tk.FLAT)
        self.event_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        self.event_entry.insert(0, "Add new event...")
        self.event_entry.bind("<FocusIn>", lambda e: self.event_entry.delete(0, tk.END) 
                            if self.event_entry.get() == "Add new event..." else None)
        self.event_entry.bind("<FocusOut>", lambda e: self.event_entry.insert(0, "Add new event...") 
                             if self.event_entry.get() == "" else None)
        self.event_entry.bind("<Return>", lambda e: self.add_event())
        
        # Add button
        add_btn = tk.Button(event_frame, text="Add", font=("Arial", 12), 
                          bg=self.accent_color, fg=self.text_color,
                          activebackground=self.accent_color, activeforeground=self.text_color,
                          relief=tk.FLAT, cursor="hand2", command=self.add_event)
        add_btn.pack(side=tk.RIGHT, padx=5, ipadx=15, ipady=5)

    def update_calendar(self):
        # Get first day of the month and number of days
        year = self.selected_date.year
        month = self.selected_date.month
        
        first_day = datetime.date(year, month, 1)
        last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])
        
        # Update month label
        self.month_label.config(text=self.get_month_year_str())
        
        # Clear all buttons
        for button in self.cal_buttons:
            button.config(text="", state=tk.DISABLED, bg=self.secondary_color)
        
        # Calculate which button to start with (Monday is 0 in Python's calendar)
        start_idx = (first_day.weekday()) % 7
        
        # Fill in the calendar buttons
        for i in range(last_day.day):
            day = i + 1
            date = datetime.date(year, month, day)
            button = self.cal_buttons[start_idx + i]
            
            button.config(text=str(day), state=tk.NORMAL)
            
            # Highlight today
            if date == datetime.date.today():
                button.config(bg="#206694")  # Highlight today with a different color
            
            # Highlight selected date
            if date == self.selected_date:
                button.config(bg=self.accent_color)
            
            # Check if date has events
            if self.has_events(date):
                button.config(fg="#FFD700")  # Gold color for days with events
            
            # Configure command with a lambda to capture the current value of day
            button.config(command=lambda d=date: self.select_date(d))

    def select_date(self, date):
        self.selected_date = date
        self.update_calendar()
        self.display_events_for_date(date)
        self.date_label.config(text=self.format_date(date))

    def display_events_for_date(self, date):
        # Clear current events
        self.events_list.delete(0, tk.END)
        
        # Format date string for dict lookup
        date_str = date.strftime("%Y-%m-%d")
        
        # Get events for this date and sort by time
        day_events = self.events.get(date_str, [])
        day_events.sort(key=lambda x: x['time'])
        
        # Display events
        for event in day_events:
            time_str = event['time']
            duration_str = f"{event['duration']} min"
            event_text = f"{time_str} ({duration_str}): {event['title']}"
            self.events_list.insert(tk.END, event_text)

    def add_event(self):
        event_title = self.event_entry.get()
        if event_title == "Add new event...":
            return
        
        # Get time
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            time_str = f"{hour:02d}:{minute:02d}"
        except ValueError:
            messagebox.showerror("Invalid Time", "Please enter a valid time.")
            return
        
        # Get duration
        try:
            duration = int(self.duration_var.get())
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Duration", "Please enter a valid duration.")
            return
        
        # Create event
        date_str = self.selected_date.strftime("%Y-%m-%d")
        if date_str not in self.events:
            self.events[date_str] = []
        
        new_event = {
            'title': event_title,
            'time': time_str,
            'duration': duration
        }
        
        self.events[date_str].append(new_event)
        self.save_events()
        
        # Update display
        self.display_events_for_date(self.selected_date)
        self.update_calendar()
        
        # Clear entry
        self.event_entry.delete(0, tk.END)
        self.event_entry.insert(0, "Add new event...")

    def edit_event(self, event):
        # Get selected event
        if not self.events_list.curselection():
            return
        
        selected_idx = self.events_list.curselection()[0]
        date_str = self.selected_date.strftime("%Y-%m-%d")
        
        if date_str not in self.events or selected_idx >= len(self.events[date_str]):
            return
        
        event = self.events[date_str][selected_idx]
        
        # Create dialog
        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title("Edit Event")
        edit_dialog.geometry("400x200")
        edit_dialog.configure(bg=self.bg_color)
        edit_dialog.resizable(False, False)
        
        # Event title
        tk.Label(edit_dialog, text="Event Title:", bg=self.bg_color, fg=self.text_color).pack(anchor="w", padx=10, pady=(10, 5))
        title_entry = tk.Entry(edit_dialog, bg=self.secondary_color, fg=self.text_color, 
                             insertbackground=self.text_color, font=("Arial", 12), width=30)
        title_entry.pack(fill="x", padx=10, pady=(0, 10))
        title_entry.insert(0, event['title'])
        
        # Time
        time_frame = tk.Frame(edit_dialog, bg=self.bg_color)
        time_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Label(time_frame, text="Time:", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=(0, 5))
        
        # Parse current time
        current_hour, current_minute = map(int, event['time'].split(':'))
        
        # Hour and minute selection
        hour_var = tk.StringVar(value=str(current_hour))
        hour_spinner = ttk.Spinbox(time_frame, from_=0, to=23, width=3, 
                                 textvariable=hour_var, wrap=True)
        hour_spinner.pack(side=tk.LEFT)
        
        tk.Label(time_frame, text=":", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)
        
        minute_var = tk.StringVar(value=f"{current_minute:02d}")
        minute_spinner = ttk.Spinbox(time_frame, from_=0, to=59, width=3, 
                                   textvariable=minute_var, wrap=True,
                                   format="%02.0f")
        minute_spinner.pack(side=tk.LEFT)
        
        # Duration
        tk.Label(time_frame, text="Duration (min):", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=(15, 5))
        
        duration_var = tk.StringVar(value=str(event['duration']))
        duration_spinner = ttk.Spinbox(time_frame, from_=5, to=480, width=4, 
                                     textvariable=duration_var, increment=5)
        duration_spinner.pack(side=tk.LEFT)
        
        # Buttons
        buttons_frame = tk.Frame(edit_dialog, bg=self.bg_color)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        def update_event():
            # Update event
            event['title'] = title_entry.get()
            
            try:
                hour = int(hour_var.get())
                minute = int(minute_var.get())
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
                event['time'] = f"{hour:02d}:{minute:02d}"
            except ValueError:
                messagebox.showerror("Invalid Time", "Please enter a valid time.")
                return
            
            try:
                duration = int(duration_var.get())
                if duration <= 0:
                    raise ValueError
                event['duration'] = duration
            except ValueError:
                messagebox.showerror("Invalid Duration", "Please enter a valid duration.")
                return
            
            self.save_events()
            self.display_events_for_date(self.selected_date)
            edit_dialog.destroy()
        
        def delete_event():
            self.events[date_str].pop(selected_idx)
            if not self.events[date_str]:
                del self.events[date_str]
            self.save_events()
            self.display_events_for_date(self.selected_date)
            self.update_calendar()
            edit_dialog.destroy()
        
        tk.Button(buttons_frame, text="Update", bg=self.accent_color, fg=self.text_color,
                activebackground=self.accent_color, relief=tk.FLAT,
                command=update_event).pack(side=tk.LEFT, padx=(0, 10), ipadx=10, ipady=5)
        
        tk.Button(buttons_frame, text="Delete", bg="#ed4245", fg=self.text_color,
                activebackground="#ed4245", relief=tk.FLAT,
                command=delete_event).pack(side=tk.LEFT, ipadx=10, ipady=5)
        
        tk.Button(buttons_frame, text="Cancel", bg=self.secondary_color, fg=self.text_color,
                activebackground=self.secondary_color, relief=tk.FLAT,
                command=edit_dialog.destroy).pack(side=tk.RIGHT, ipadx=10, ipady=5)

    def delete_selected_event(self, event):
        if not self.events_list.curselection():
            return
        
        selected_idx = self.events_list.curselection()[0]
        date_str = self.selected_date.strftime("%Y-%m-%d")
        
        if date_str in self.events and selected_idx < len(self.events[date_str]):
            if messagebox.askyesno("Delete Event", "Are you sure you want to delete this event?"):
                self.events[date_str].pop(selected_idx)
                if not self.events[date_str]:
                    del self.events[date_str]
                self.save_events()
                self.display_events_for_date(self.selected_date)
                self.update_calendar()

    def has_events(self, date):
        date_str = date.strftime("%Y-%m-%d")
        return date_str in self.events and len(self.events[date_str]) > 0

    def go_to_today(self):
        today = datetime.date.today()
        self.select_date(today)

    def view_this_week(self):
        today = datetime.date.today()
        self.select_date(today)
        # Future: Implement weekly view

    def view_this_month(self):
        today = datetime.date.today()
        self.selected_date = today
        self.update_calendar()
        self.display_events_for_date(today)
        self.date_label.config(text=self.format_date(today))

    def focus_add_event(self):
        self.event_entry.focus_set()
        if self.event_entry.get() == "Add new event...":
            self.event_entry.delete(0, tk.END)

    def prev_month(self):
        year = self.selected_date.year
        month = self.selected_date.month
        
        # Go to previous month
        if month == 1:
            new_month = 12
            new_year = year - 1
        else:
            new_month = month - 1
            new_year = year
        
        # Get the same day in the new month, or the last day if it doesn't exist
        day = min(self.selected_date.day, calendar.monthrange(new_year, new_month)[1])
        
        self.selected_date = datetime.date(new_year, new_month, day)
        self.update_calendar()
        self.display_events_for_date(self.selected_date)
        self.date_label.config(text=self.format_date(self.selected_date))

    def next_month(self):
        year = self.selected_date.year
        month = self.selected_date.month
        
        # Go to next month
        if month == 12:
            new_month = 1
            new_year = year + 1
        else:
            new_month = month + 1
            new_year = year
        
        # Get the same day in the new month, or the last day if it doesn't exist
        day = min(self.selected_date.day, calendar.monthrange(new_year, new_month)[1])
        
        self.selected_date = datetime.date(new_year, new_month, day)
        self.update_calendar()
        self.display_events_for_date(self.selected_date)
        self.date_label.config(text=self.format_date(self.selected_date))

    def get_month_year_str(self):
        return self.selected_date.strftime("%B %Y")

    def format_date(self, date):
        # Returns formatted date string (e.g., "Monday, January 1, 2023")
        return date.strftime("%A, %B %d, %Y")

    def load_events(self):
        # Load events from file
        file_path = "calendar_events.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_events(self):
        # Save events to file
        with open("calendar_events.json", "w") as f:
            json.dump(self.events, f, indent=4)

def main():
    # Create themed root window
    root = ThemedTk(theme="arc")
    app = CalendarApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()