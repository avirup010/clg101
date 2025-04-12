import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
from collections import Counter
import threading
from plyer import notification
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import random

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('vader_lexicon')
    nltk.data.find('stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('vader_lexicon')
    nltk.download('stopwords')

class RelationshipAdvisorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Relationship Advisor")
        self.root.geometry("900x650")
        self.root.configure(bg="#1e1e2f")  # Deep indigo base

        self.entries = self.load_entries()
        self.running = True
        self.sid = SentimentIntensityAnalyzer()

        self.create_ui()
        self.start_background_advice()

    def create_ui(self):
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Helvetica", 10, "bold"), padding=10, background="#3b3b5b", 
                       foreground="white", borderwidth=0, relief="flat")
        style.map("TButton", background=[("active", "#5a5a8a")])
        style.configure("Accent.TButton", background="#6b48ff", foreground="white")
        style.map("Accent.TButton", background=[("active", "#5439cc")])

        # Gradient background
        self.bg_canvas = tk.Canvas(self.root, bg="#1e1e2f", highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.create_gradient()

        # Header
        header_frame = tk.Frame(self.bg_canvas, bg="#28283c", bd=0)  # Converted rgba(40, 40, 60, 0.9) to hex
        header_frame.place(relx=0.5, rely=0.05, anchor="n", relwidth=0.9, relheight=0.1)
        tk.Label(header_frame, text="Relationship Advisor", font=("Helvetica", 20, "bold"), 
                bg="#28283c", fg="#ffffff").pack(pady=15)

        # Main container
        main_container = tk.Frame(self.bg_canvas, bg="#1e1e32", bd=0)  # Converted rgba(30, 30, 50, 0.85) to hex
        main_container.place(relx=0.5, rely=0.2, anchor="n", relwidth=0.9, relheight=0.75)

        # Input section
        input_frame = tk.Frame(main_container, bg="#1e1e32", bd=0)
        input_frame.pack(fill="x", pady=(20, 10), padx=20)

        self.entry_text = tk.Text(input_frame, font=("Helvetica", 12), bg="#3b3b5b", 
                                 fg="white", insertbackground="white", bd=0, height=4, wrap="word")
        self.entry_text.insert("1.0", "Describe your relationship situation...")
        self.entry_text.bind("<FocusIn>", lambda e: self.clear_placeholder(self.entry_text, "Describe your relationship situation..."))
        self.entry_text.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=5)

        ttk.Button(input_frame, text="Submit", style="Accent.TButton", 
                  command=self.log_entry).pack(side="right", pady=5)

        # Tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Entries tab
        self.entries_frame = tk.Frame(notebook, bg="#1e1e32")
        notebook.add(self.entries_frame, text="Entries")

        self.entries_canvas = tk.Canvas(self.entries_frame, bg="#1e1e32", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.entries_frame, orient="vertical", command=self.entries_canvas.yview)
        self.entries_scrollable = tk.Frame(self.entries_canvas, bg="#1e1e32")

        self.entries_scrollable.bind(
            "<Configure>",
            lambda e: self.entries_canvas.configure(scrollregion=self.entries_canvas.bbox("all"))
        )
        self.entries_canvas.create_window((0, 0), window=self.entries_scrollable, anchor="nw")
        self.entries_canvas.configure(yscrollcommand=scrollbar.set)
        self.entries_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Advice tab
        self.advice_frame = tk.Frame(notebook, bg="#1e1e32")
        notebook.add(self.advice_frame, text="Advice")

        self.update_entries_display()

    def create_gradient(self):
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        for i in range(height):
            r = int(30 + (i / height) * 20)
            g = int(30 + (i / height) * 20)
            b = int(47 + (i / height) * 40)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.bg_canvas.create_line(0, i, width, i, fill=color)

    def clear_placeholder(self, widget, placeholder):
        if widget.get("1.0", "end-1c") == placeholder:
            widget.delete("1.0", tk.END)

    def load_entries(self):
        try:
            with open("relationship_entries.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_entries(self):
        with open("relationship_entries.json", "w") as f:
            json.dump(self.entries, f)

    def log_entry(self):
        entry_text = self.entry_text.get("1.0", "end-1c").strip()
        if not entry_text or entry_text == "Describe your relationship situation...":
            messagebox.showerror("Error", "Please enter a description")
            return

        entry = {
            "text": entry_text,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analyzed": False
        }
        self.entries.append(entry)
        self.save_entries()
        self.update_entries_display()
        
        self.fade_entry(self.entry_text, "Describe your relationship situation...")

    def fade_entry(self, entry, text):
        entry.delete("1.0", tk.END)
        entry.insert("1.0", text)
        entry.config(fg="#808080")

    def update_entries_display(self):
        for widget in self.entries_scrollable.winfo_children():
            widget.destroy()

        for i, entry in enumerate(self.entries):
            entry_frame = tk.Frame(self.entries_scrollable, bg="#3b3b5b", bd=0)
            entry_frame.pack(fill="x", pady=5, padx=5)

            entry_frame.place(relx=1.0, rely=(i * 0.1), anchor="ne")
            entry_frame.after(100 + (i * 100), lambda f=entry_frame: self.animate_card(f))

            tk.Label(entry_frame, text=entry["date"], font=("Helvetica", 10), 
                    bg="#3b3b5b", fg="#b0b0b0").pack(side="left", padx=15, pady=10)
            tk.Label(entry_frame, text=entry["text"][:50] + "..." if len(entry["text"]) > 50 else entry["text"], 
                    font=("Helvetica", 11, "bold"), bg="#3b3b5b", fg="#ffffff").pack(side="left", padx=15, pady=10)
            
            ttk.Button(entry_frame, text="Delete", 
                      command=lambda idx=i: self.delete_entry(idx)).pack(side="right", padx=10, pady=5)

    def animate_card(self, frame):
        def move_frame(x):
            if x > 0:
                frame.place(relx=x/100, rely=frame.winfo_y()/self.entries_scrollable.winfo_height())
                frame.after(8, lambda: move_frame(x-5))
            else:
                frame.place(relx=0, rely=frame.winfo_y()/self.entries_scrollable.winfo_height())
        
        move_frame(100)

    def delete_entry(self, index):
        self.entries.pop(index)
        self.save_entries()
        self.update_entries_display()

    def analyze_relationship(self):
        if not self.entries:
            return

        unanalyzed_text = " ".join(entry["text"] for entry in self.entries if not entry["analyzed"])
        if not unanalyzed_text:
            return

        # Tokenize and clean
        tokens = word_tokenize(unanalyzed_text.lower())
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
        word_freq = Counter(filtered_tokens).most_common(5)

        # Sentiment analysis
        sentiment_scores = self.sid.polarity_scores(unanalyzed_text)
        compound_score = sentiment_scores['compound']
        sentiment = "Positive" if compound_score > 0.1 else "Negative" if compound_score < -0.1 else "Neutral"

        # Generate advice
        key_themes = [word for word, _ in word_freq]
        advice = self.generate_advice(sentiment, key_themes, unanalyzed_text)

        # Update advice tab
        for widget in self.advice_frame.winfo_children():
            widget.destroy()

        tk.Label(self.advice_frame, text="Relationship Insights", font=("Helvetica", 14, "bold"), 
                bg="#1e1e32", fg="#ffffff").pack(pady=15)

        sentiment_frame = tk.Frame(self.advice_frame, bg="#3b3b5b")
        sentiment_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(sentiment_frame, text=f"Current Vibe: {sentiment} (Score: {compound_score:.2f})", 
                font=("Helvetica", 12, "bold"), bg="#3b3b5b", fg="#ffffff").pack(pady=10)

        themes_frame = tk.Frame(self.advice_frame, bg="#3b3b5b")
        themes_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(themes_frame, text="Key Themes:", font=("Helvetica", 12, "bold"), 
                bg="#3b3b5b", fg="#ffffff").pack(pady=5)
        for word, count in word_freq:
            tk.Label(themes_frame, text=f"{word}: {count} times", bg="#3b3b5b", fg="#b0b0b0").pack(padx=30)

        advice_frame = tk.Frame(self.advice_frame, bg="#3b3b5b")
        advice_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(advice_frame, text="AI-Generated Advice:", font=("Helvetica", 12, "bold"), 
                bg="#3b3b5b", fg="#ffffff").pack(pady=5)
        tk.Label(advice_frame, text=advice, bg="#3b3b5b", fg="#d0d0ff", wraplength=600).pack(padx=30, pady=5)

        # Mark as analyzed
        for entry in self.entries:
            if not entry["analyzed"]:
                entry["analyzed"] = True
        self.save_entries()

        notification.notify(
            title="Relationship Advice",
            message=f"Vibe: {sentiment}\nAdvice: {advice[:50]}..." if len(advice) > 50 else advice,
            timeout=10
        )

    def generate_advice(self, sentiment, themes, text):
        advice_parts = []

        # Sentiment-based context
        if sentiment == "Positive":
            advice_parts.append("Your relationship seems to be in a good place right now.")
        elif sentiment == "Negative":
            advice_parts.append("It sounds like there are some difficulties in your relationship at the moment.")
        else:
            advice_parts.append("Your relationship has a balanced mix of experiences currently.")

        # Theme-based insights
        if themes:
            advice_parts.append(f"Notably, '{themes[0]}' appears frequently in your descriptions.")
            if "conflict" in themes or "fight" in themes or "argue" in themes:
                advice_parts.append("To address any tension, consider a calm, open conversation to uncover underlying issues.")
            elif "love" in themes or "happy" in themes or "good" in themes:
                advice_parts.append("Build on this positivity by sharing appreciation or planning a meaningful activity together.")
            elif "trust" in themes or "communication" in themes:
                advice_parts.append("Strengthening trust and communication could be a key focus—try being fully present in your next talk.")
            else:
                advice_parts.append(f"Explore what '{themes[0]}' signifies for you; it might reveal what’s most on your mind.")

        # Text-specific analysis
        if "not" in text.lower() and "talk" in text.lower():
            advice_parts.append("If communication is lacking, start with small, honest exchanges to rebuild dialogue.")
        elif "feel" in text.lower() and "alone" in text.lower():
            advice_parts.append("Feeling isolated can be hard—reach out to your partner or a friend to bridge that gap.")
        elif "time" in text.lower():
            advice_parts.append("Time seems significant; carving out dedicated moments together might help.")

        # Encouragement
        advice_parts.append("Take it one step at a time and see how your dynamic shifts in the coming days.")

        return " ".join(advice_parts)

    def start_background_advice(self):
        def run_advice():
            while self.running:
                if any(not entry["analyzed"] for entry in self.entries):
                    self.analyze_relationship()
                time.sleep(300)
        
        self.advice_thread = threading.Thread(target=run_advice, daemon=True)
        self.advice_thread.start()

    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RelationshipAdvisorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()