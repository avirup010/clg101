import customtkinter as ctk
from typing import List
import random
import time
import math
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ModernTypingTest:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Modern Typing Test")
        self.root.geometry("1200x1080")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Sentences categorized by length
        self.sentences = {
            'small': [
                "The quick brown fox jumps over the lazy dog.",
                "Pack my box with five dozen liquor jugs.",
                "How vexingly quick daft zebras jump!"
            ],
            'medium': [
                "The advantage of the emotions is that they lead us astray, and the advantage of science is that it is not emotional. The crow wished everything was black, the owl that everything was white.",
                "A wonderful serenity has taken possession of my entire soul, like these sweet mornings of spring which I enjoy with my whole heart.",
                "Life is like a box of chocolates. You never know what you're going to get. Success is not final, failure is not fatal: it is the courage to continue that counts."
            ],
            'huge': [
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "The technological revolution of the twentieth century has allowed human beings to break free of the Earth's atmosphere and venture into space. This achievement represents one of humanity's greatest accomplishments, demonstrating our ability to overcome seemingly insurmountable challenges through innovation, determination, and collaborative effort.",
                "The complexity of modern society demands a sophisticated understanding of interconnected systems. From economic markets to ecological networks, every aspect of our world is intricately linked. Understanding these connections requires both broad knowledge and specialized expertise."
            ]
        }

        self.current_text = ""
        self.start_time = None
        self.is_test_active = False
        self.animation_after_id = None
        self.wpm_history = []
        self.time_history = []
        self.selected_size = 'medium'
        
        self.setup_ui()
        self.bind_shortcuts()
        self.new_test()

    def setup_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray16"))
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Size selection frame
        self.size_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.size_frame.pack(fill="x", padx=20, pady=10)

        self.size_label = ctk.CTkLabel(
            self.size_frame,
            text="Select Text Length:",
            font=("Helvetica", 14)
        )
        self.size_label.pack(side="left", padx=10)

        self.size_var = ctk.StringVar(value="medium")
        self.size_menu = ctk.CTkOptionMenu(
            self.size_frame,
            values=["small", "medium", "huge"],
            variable=self.size_var,
            command=self.change_size,
            font=("Helvetica", 14)
        )
        self.size_menu.pack(side="left", padx=10)

        # Stats frame
        self.stats_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=("gray85", "gray17"),
            corner_radius=10
        )
        self.stats_frame.pack(fill="x", padx=20, pady=10)

        # WPM Progress
        self.wpm_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        self.wpm_frame.pack(side="left", expand=True, padx=10, pady=5)
        
        self.wpm_label = ctk.CTkLabel(
            self.wpm_frame,
            text="0 WPM",
            font=("Helvetica", 18)
        )
        self.wpm_label.pack(pady=2)
        
        self.wpm_progress = ctk.CTkProgressBar(
            self.wpm_frame,
            width=200,
            height=8
        )
        self.wpm_progress.pack(pady=2)
        self.wpm_progress.set(0)

        # Accuracy Progress
        self.accuracy_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        self.accuracy_frame.pack(side="left", expand=True, padx=10, pady=5)
        
        self.accuracy_label = ctk.CTkLabel(
            self.accuracy_frame,
            text="0% Accuracy",
            font=("Helvetica", 18)
        )
        self.accuracy_label.pack(pady=2)
        
        self.accuracy_progress = ctk.CTkProgressBar(
            self.accuracy_frame,
            width=200,
            height=8
        )
        self.accuracy_progress.pack(pady=2)
        self.accuracy_progress.set(0)

        # Target text display
        self.target_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=("gray85", "gray17"),
            corner_radius=10
        )
        self.target_frame.pack(fill="x", padx=20, pady=10)

        self.target_label = ctk.CTkLabel(
            self.target_frame,
            text="",
            wraplength=1100,
            font=("Helvetica", 16),
            pady=20
        )
        self.target_label.pack()

        # Input field
        self.input_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=("gray85", "gray17"),
            corner_radius=10
        )
        self.input_frame.pack(fill="x", padx=20, pady=10)

        self.input_text = ctk.CTkTextbox(
            self.input_frame,
            height=100,
            font=("Helvetica", 16),
            corner_radius=8
        )
        self.input_text.pack(fill="x", padx=10, pady=10)

        # Graph frame
        self.graph_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=("gray85", "gray17"),
            corner_radius=10,
            height=200
        )
        self.graph_frame.pack(fill="x", padx=20, pady=10)

        # Initialize matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 3))
        self.fig.patch.set_facecolor('#2C3E50')
        self.ax.set_facecolor('#2C3E50')
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.set_title('WPM Progress', color='white')
        self.ax.set_xlabel('Time (seconds)', color='white')
        self.ax.set_ylabel('WPM', color='white')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Controls
        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=20, pady=10)

        self.new_test_btn = ctk.CTkButton(
            self.controls_frame,
            text="New Test (ESC)",
            command=self.new_test,
            font=("Helvetica", 14)
        )
        self.new_test_btn.pack(side="left", padx=10)

        self.restart_btn = ctk.CTkButton(
            self.controls_frame,
            text="Restart (Ctrl+R)",
            command=self.new_test,
            font=("Helvetica", 14)
        )
        self.restart_btn.pack(side="left", padx=10)

    def calculate_wpm(self, elapsed_time: float, typed_text: str, target_text: str) -> float:
        """
        Calculate WPM based on completed correct words
        """
        if elapsed_time == 0:
            return 0
            
        typed_words = typed_text.split()
        target_words = target_text.split()
        
        # Count correctly typed complete words
        correct_words = 0
        for i, typed_word in enumerate(typed_words):
            if i < len(target_words) and typed_word == target_words[i]:
                correct_words += 1
        
        # WPM = (correct words typed / time in minutes)
        minutes = elapsed_time / 60
        wpm = correct_words / minutes if minutes > 0 else 0
        
        return round(wpm)

    def calculate_accuracy(self, typed_text: str, target_text: str) -> float:
        """
        Calculate accuracy based on Levenshtein distance for each word
        """
        typed_words = typed_text.split()
        target_words = target_text.split()
        
        if not typed_words:
            return 0.0

        total_similarity = 0
        words_compared = 0
        
        # Compare each typed word with its corresponding target word
        for i, typed_word in enumerate(typed_words):
            if i < len(target_words):
                target_word = target_words[i]
                distance = self.levenshtein_distance(typed_word.lower(), target_word.lower())
                max_length = max(len(typed_word), len(target_word))
                similarity = (max_length - distance) / max_length if max_length > 0 else 0
                total_similarity += similarity
                words_compared += 1
        
        # Calculate overall accuracy
        accuracy = (total_similarity / words_compared) * 100 if words_compared > 0 else 0
        return round(accuracy, 1)

    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate the minimum edit distance between two strings
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def change_size(self, size):
        self.selected_size = size
        self.new_test()

    def update_graph(self):
        self.ax.clear()
        self.ax.set_facecolor('#2C3E50')
        self.ax.tick_params(colors='white')
        self.ax.set_title('WPM Progress', color='white')
        self.ax.set_xlabel('Time (seconds)', color='white')
        self.ax.set_ylabel('WPM', color='white')
        
        if self.time_history and self.wpm_history:
            self.ax.plot(self.time_history, self.wpm_history, 
                        color='#2ECC71', linewidth=2, marker='o')
            
            # Add trend line
            z = np.polyfit(self.time_history, self.wpm_history, 1)
            p = np.poly1d(z)
            self.ax.plot(self.time_history, p(self.time_history), 
                        color='#E74C3C', linestyle='--', alpha=0.8)

        self.canvas.draw()

    def bind_shortcuts(self):
        self.root.bind("<Escape>", lambda e: self.new_test())
        self.root.bind("<Control-r>", lambda e: self.new_test())
        self.input_text.bind("<KeyRelease>", self.check_input)

    def new_test(self):
        self.current_text = random.choice(self.sentences[self.selected_size])
        self.target_label.configure(text=self.current_text)
        self.input_text.delete("0.0", "end")
        self.wpm_label.configure(text="0 WPM")
        self.accuracy_label.configure(text="0% Accuracy")
        self.wpm_progress.set(0)
        self.accuracy_progress.set(0)
        self.start_time = None
        self.is_test_active = False
        self.wpm_history = []
        self.time_history = []
        self.update_graph()
        self.input_text.focus()

    def check_input(self, event):
        if not self.is_test_active:
            self.start_time = time.time()
            self.is_test_active = True

        current_input = self.input_text.get("0.0", "end-1c")
        
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            wpm = self.calculate_wpm(elapsed_time, current_input, self.current_text)
            accuracy = self.calculate_accuracy(current_input, self.current_text)
            
            self.wpm_label.configure(text=f"{wpm} WPM")
            self.accuracy_label.configure(text=f"{accuracy}% Accuracy")
            self.wpm_progress.set(min(wpm / 100, 1.0))
            self.accuracy_progress.set(accuracy / 100)

            # Update WPM history
            self.time_history.append(round(elapsed_time, 1))
            self.wpm_history.append(wpm)
            self.update_graph()

            # Visual feedback for current word
            self.highlight_current_word(current_input)

        if current_input == self.current_text:
            self.animate_completion()

    def highlight_current_word(self, current_input: str):
        """
        Provide visual feedback for the current word being typed
        """
        typed_words = current_input.split()
        target_words = self.current_text.split()
        
        if not typed_words:
            return
            
        current_word_index = len(typed_words) - 1
        if current_word_index < len(target_words):
            current_typed = typed_words[-1]
            current_target = target_words[current_word_index]
            
            # Calculate similarity for the current word
            distance = self.levenshtein_distance(current_typed.lower(), current_target.lower())
            max_length = max(len(current_typed), len(current_target))
            similarity = (max_length - distance) / max_length if max_length > 0 else 0
            
            # Update input text color based on similarity
            if similarity == 1:  # Perfect match
                self.input_text.configure(text_color="#2ECC71")  # Green
            elif similarity > 0.5:  # Close match
                self.input_text.configure(text_color="#F1C40F")  # Yellow
            else:  # Poor match
                self.input_text.configure(text_color="#E74C3C")  # Red

    def animate_completion(self):
        def flash(count):
            if count < 3:  # Flash 3 times
                self.input_text.configure(fg_color=("#27AE60", "#2ECC71"))
                self.root.after(100, lambda: self.input_text.configure(
                    fg_color=("gray85", "gray17")))
                self.root.after(200, lambda: flash(count + 1))
        flash(0)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernTypingTest()
    app.run()
    