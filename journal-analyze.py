import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
from collections import Counter
import threading
from plyer import notification

class DreamJournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dream Journal Analyzer")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a1a")

        self.dreams = self.load_dreams()
        self.running = True

        self.create_ui()
        self.start_background_analysis()

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
        tk.Label(header_frame, text="Dream Journal Analyzer", font=("Helvetica", 18, "bold"), 
                bg="#252526", fg="#ffffff").pack(pady=15)

        # Main container
        main_container = tk.Frame(self.root, bg="#1a1a1a")
        main_container.pack(pady=20, padx=20, fill="both", expand=True)

        # Input section
        input_frame = tk.Frame(main_container, bg="#252526", bd=0)
        input_frame.pack(fill="x", pady=(0, 20))

        self.dream_entry = tk.Text(input_frame, font=("Helvetica", 11), bg="#3d3d3d", 
                                 fg="white", insertbackground="white", bd=0, height=5, wrap="word")
        self.dream_entry.insert("1.0", "Enter your dream here...")
        self.dream_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.dream_entry, "Enter your dream here..."))
        self.dream_entry.pack(side="left", padx=5, pady=10, fill="x", expand=True)

        ttk.Button(input_frame, text="Log Dream", style="Accent.TButton", 
                  command=self.log_dream).pack(side="right", padx=5, pady=10)

        # Tabs for dreams and analysis
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill="both", expand=True)

        # Dreams tab
        self.dreams_frame = tk.Frame(notebook, bg="#1a1a1a")
        notebook.add(self.dreams_frame, text="Dreams")

        self.dreams_canvas = tk.Canvas(self.dreams_frame, bg="#1a1a1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.dreams_frame, orient="vertical", command=self.dreams_canvas.yview)
        self.dreams_scrollable = tk.Frame(self.dreams_canvas, bg="#1a1a1a")

        self.dreams_scrollable.bind(
            "<Configure>",
            lambda e: self.dreams_canvas.configure(scrollregion=self.dreams_canvas.bbox("all"))
        )
        self.dreams_canvas.create_window((0, 0), window=self.dreams_scrollable, anchor="nw")
        self.dreams_canvas.configure(yscrollcommand=scrollbar.set)
        self.dreams_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Analysis tab
        self.analysis_frame = tk.Frame(notebook, bg="#1a1a1a")
        notebook.add(self.analysis_frame, text="Analysis")

        self.update_dreams_display()

    def clear_placeholder(self, widget, placeholder):
        if widget.get("1.0", "end-1c") == placeholder:
            widget.delete("1.0", tk.END)

    def load_dreams(self):
        try:
            with open("dreams.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_dreams(self):
        with open("dreams.json", "w") as f:
            json.dump(self.dreams, f)

    def log_dream(self):
        dream_text = self.dream_entry.get("1.0", "end-1c").strip()
        if not dream_text or dream_text == "Enter your dream here...":
            messagebox.showerror("Error", "Please enter a dream description")
            return

        dream = {
            "text": dream_text,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analyzed": False
        }
        self.dreams.append(dream)
        self.save_dreams()
        self.update_dreams_display()
        
        self.fade_entry(self.dream_entry, "Enter your dream here...")

    def fade_entry(self, entry, text):
        entry.delete("1.0", tk.END)
        entry.insert("1.0", text)
        entry.config(fg="#808080")

    def update_dreams_display(self):
        for widget in self.dreams_scrollable.winfo_children():
            widget.destroy()

        for i, dream in enumerate(self.dreams):
            dream_frame = tk.Frame(self.dreams_scrollable, bg="#252526", bd=0)
            dream_frame.pack(fill="x", pady=5, padx=5)

            dream_frame.place(relx=1.0, rely=(i * 0.1), anchor="ne")
            dream_frame.after(100 + (i * 100), lambda f=dream_frame: self.animate_card(f))

            tk.Label(dream_frame, text=dream["date"], font=("Helvetica", 10), 
                    bg="#252526", fg="#b0b0b0").pack(side="left", padx=15, pady=5)
            tk.Label(dream_frame, text=dream["text"][:50] + "..." if len(dream["text"]) > 50 else dream["text"], 
                    font=("Helvetica", 11, "bold"), bg="#252526", fg="#ffffff").pack(side="left", padx=15, pady=5)
            
            ttk.Button(dream_frame, text="Delete", 
                      command=lambda idx=i: self.delete_dream(idx)).pack(side="right", padx=10, pady=5)

    def animate_card(self, frame):
        def move_frame(x):
            if x > 0:
                frame.place(relx=x/100, rely=frame.winfo_y()/self.dreams_scrollable.winfo_height())
                frame.after(10, lambda: move_frame(x-5))
            else:
                frame.place(relx=0, rely=frame.winfo_y()/self.dreams_scrollable.winfo_height())
        
        move_frame(100)

    def delete_dream(self, index):
        self.dreams.pop(index)
        self.save_dreams()
        self.update_dreams_display()

    def analyze_dreams(self):
        if not self.dreams:
            return

        # Simple AI analysis: word frequency and basic sentiment
        all_text = " ".join(dream["text"] for dream in self.dreams if not dream["analyzed"])
        words = all_text.lower().split()
        word_freq = Counter(words).most_common(10)

        # Basic sentiment analysis (positive/negative/neutral words)
        positive_words = {"happy", "good", "love", "peace", "joy"}
        negative_words = {"fear", "bad", "sad", "angry", "death"}
        positive_count = sum(word in positive_words for word in words)
        negative_count = sum(word in negative_words for word in words)
        
        sentiment = "Neutral"
        if positive_count > negative_count:
            sentiment = "Positive"
        elif negative_count > positive_count:
            sentiment = "Negative"

        # Update analysis tab
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()

        tk.Label(self.analysis_frame, text="Dream Analysis", font=("Helvetica", 14, "bold"), 
                bg="#1a1a1a", fg="#ffffff").pack(pady=10)

        # Word frequency
        freq_frame = tk.Frame(self.analysis_frame, bg="#252526")
        freq_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(freq_frame, text="Common Themes (Top Words):", font=("Helvetica", 11, "bold"), 
                bg="#252526", fg="#ffffff").pack(pady=5)
        for word, count in word_freq:
            tk.Label(freq_frame, text=f"{word}: {count} times", bg="#252526", fg="#b0b0b0").pack(padx=20)

        # Sentiment
        sentiment_frame = tk.Frame(self.analysis_frame, bg="#252526")
        sentiment_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(sentiment_frame, text=f"Overall Sentiment: {sentiment}", font=("Helvetica", 11, "bold"), 
                bg="#252526", fg="#ffffff").pack(pady=5)

        # Mark dreams as analyzed
        for dream in self.dreams:
            if not dream["analyzed"]:
                dream["analyzed"] = True
        self.save_dreams()

        # Notification
        notification.notify(
            title="Dream Analysis Complete",
            message=f"Sentiment: {sentiment}\nTop theme: {word_freq[0][0]}",
            timeout=10
        )

    def start_background_analysis(self):
        def run_analysis():
            while self.running:
                if any(not dream["analyzed"] for dream in self.dreams):
                    self.analyze_dreams()
                time.sleep(300)  # Check every 5 minutes
        
        self.analysis_thread = threading.Thread(target=run_analysis, daemon=True)
        self.analysis_thread.start()

    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DreamJournalApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()