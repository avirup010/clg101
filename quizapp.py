import tkinter as tk
from tkinter import ttk
import random
from ttkthemes import ThemedTk
import time

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Master")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Sleek, modern color scheme
        self.colors = {
            "background": "#0d0d1a",    # Deep dark blue
            "primary": "#8a4af3",       # Neon purple
            "primary_dark": "#6a3ab2",  # Darker purple for hover
            "text": "#d9d9e6",          # Soft light gray
            "success": "#00e6b8",       # Bright teal
            "error": "#ff4d4d",         # Vibrant red
            "warning": "#ffaa33",       # Neon orange
            "option_bg": "#1a1a2e",     # Dark option background
            "option_hover": "#252540",  # Subtle hover effect
            "button_gradient": "#b366ff" # Gradient accent for buttons
        }

        # Style setup
        self.style = ttk.Style()
        self.style.theme_use("arc")
        self.style.configure("TFrame", background=self.colors["background"])
        self.style.configure("TButton", font=("Helvetica", 12, "bold"), borderwidth=0, padding=10, foreground=self.colors["text"])
        self.style.configure("TLabel", font=("Helvetica", 12), background=self.colors["background"], foreground=self.colors["text"])
        self.style.configure("Title.TLabel", font=("Helvetica", 28, "bold"), foreground=self.colors["primary"])
        self.style.configure("Question.TLabel", font=("Helvetica", 16, "bold"), foreground=self.colors["text"], wraplength=700)
        self.style.configure("Stats.TLabel", font=("Helvetica", 11), foreground=self.colors["text"])
        self.style.configure("Feedback.TLabel", font=("Helvetica", 13), foreground=self.colors["text"], wraplength=650, justify="center")
        self.style.configure("TRadiobutton", background=self.colors["option_bg"], foreground=self.colors["text"])

        # Quiz variables
        self.categories = ["General Knowledge", "Science", "History", "Geography", "Technology", "UI/UX Design"]
        self.selected_category = tk.StringVar(value="General Knowledge")
        self.questions = []
        self.current_question = 0
        self.score = 0
        self.timer_seconds = 15
        self.timer_running = False

        # Frames
        self.main_frame = ttk.Frame(self.root, padding=30, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.header_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        self.content_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        self.footer_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.footer_frame.pack(fill=tk.X, pady=(20, 0))

        self.setup_welcome_screen()
        self.load_questions()

    def load_questions(self):
        # Sample questions (expand as needed)
        self.all_questions = {
            "General Knowledge": [
                {"question": "Which planet in our solar system is known as the Red Planet?", "options": ["Venus", "Mars", "Jupiter", "Mercury"], "correct": 1, "explanation": "Mars is known as the Red Planet due to iron oxide (rust) on its surface."},
                {"question": "What is the tallest mountain in the world?", "options": ["K2", "Mount Kilimanjaro", "Mount Everest", "Makalu"], "correct": 2, "explanation": "Mount Everest is the tallest, at 8,848.86 meters."}
            ],
            # Add other categories here
        }

    def fade_in(self, widget, alpha=0.0):
        """Fade in effect for widgets."""
        if alpha < 1.0:
            alpha += 0.15
            widget.config(foreground=f"#{int(int('d9d9e6'[1:3], 16) * alpha):02x}{int(int('d9d9e6'[3:5], 16) * alpha):02x}{int(int('d9d9e6'[5:], 16) * alpha):02x}")
            self.root.after(40, lambda: self.fade_in(widget, alpha))

    def create_modern_button(self, parent, text, command):
        """Create a modern gradient-style button."""
        btn_frame = tk.Frame(parent, bg=self.colors["primary"], bd=0, relief="flat")
        btn = tk.Button(btn_frame, text=text, command=command, font=("Helvetica", 12, "bold"), bg=self.colors["primary"], fg=self.colors["text"], 
                        activebackground=self.colors["primary_dark"], activeforeground=self.colors["text"], bd=0, relief="flat", padx=20, pady=10)
        btn.pack(fill=tk.BOTH, expand=True)
        
        def on_enter(e):
            btn_frame.config(bg=self.colors["primary_dark"])
            btn.config(bg=self.colors["primary_dark"], font=("Helvetica", 13, "bold"))
        
        def on_leave(e):
            btn_frame.config(bg=self.colors["primary"])
            btn.config(bg=self.colors["primary"], font=("Helvetica", 12, "bold"))
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn_frame

    def setup_welcome_screen(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        title_label = ttk.Label(self.content_frame, text="Quiz Master", style="Title.TLabel")
        title_label.pack(pady=(70, 20))
        self.fade_in(title_label)

        welcome_msg = ttk.Label(self.content_frame, text="Challenge yourself with a sleek, timed quiz!", font=("Helvetica", 14))
        welcome_msg.pack(pady=20)

        category_frame = ttk.Frame(self.content_frame, style="TFrame")
        category_frame.pack(pady=30)
        ttk.Label(category_frame, text="Category:", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT, padx=(0, 15))
        category_menu = ttk.Combobox(category_frame, textvariable=self.selected_category, values=self.categories, state="readonly", width=25, font=("Helvetica", 11))
        category_menu.pack(side=tk.LEFT)

        start_btn = self.create_modern_button(self.content_frame, "Start Quiz", self.start_quiz)
        start_btn.pack(pady=40)

    def start_quiz(self):
        self.current_question = 0
        self.score = 0
        self.questions = self.all_questions.get(self.selected_category.get(), [])
        if len(self.questions) < 5:
            extra_needed = 5 - len(self.questions)
            other_questions = [q for cat, qs in self.all_questions.items() if cat != self.selected_category.get() for q in qs]
            random.shuffle(other_questions)
            self.questions.extend(other_questions[:extra_needed])
        random.shuffle(self.questions)
        self.display_question()

    def display_question(self):
        for widget in self.content_frame.winfo_children() + self.header_frame.winfo_children() + self.footer_frame.winfo_children():
            widget.destroy()

        if self.current_question < len(self.questions):
            question_data = self.questions[self.current_question]

            # Header
            progress_frame = ttk.Frame(self.header_frame)
            progress_frame.pack(fill=tk.X, pady=10)
            ttk.Label(progress_frame, text=f"Q{self.current_question + 1}/{len(self.questions)}", style="Stats.TLabel").pack(side=tk.LEFT)
            ttk.Label(progress_frame, text=f"Score: {self.score}", style="Stats.TLabel").pack(side=tk.RIGHT)
            progress = ttk.Progressbar(self.header_frame, length=400, maximum=len(self.questions), value=self.current_question + 1, mode="determinate")
            self.style.configure("TProgressbar", troughcolor=self.colors["option_bg"], background=self.colors["primary"])
            progress.pack(pady=10)

            # Timer
            self.timer_seconds = 15
            self.timer_label = ttk.Label(self.header_frame, text=f"Time: {self.timer_seconds}s", style="Stats.TLabel")
            self.timer_label.pack(side=tk.RIGHT, padx=20)

            # Question
            question_label = ttk.Label(self.content_frame, text=question_data["question"], style="Question.TLabel")
            question_label.pack(pady=(40, 40))

            # Options (no boxes, just sleek radio buttons)
            self.selected_option = tk.IntVar(value=-1)
            options_frame = ttk.Frame(self.content_frame, style="TFrame")
            options_frame.pack(fill=tk.X, padx=60)
            for i, option_text in enumerate(question_data["options"]):
                opt = ttk.Radiobutton(options_frame, text=option_text, variable=self.selected_option, value=i, style="TRadiobutton")
                opt.pack(anchor="w", pady=12, padx=20)
                opt.configure(cursor="hand2")

            # Submit button
            submit_btn = self.create_modern_button(self.footer_frame, "Submit", self.check_answer)
            submit_btn.pack(side=tk.RIGHT, pady=15)

            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.timer_label.config(text=f"Time: {self.timer_seconds}s")
            if self.timer_seconds <= 5:
                self.timer_label.config(foreground=self.colors["warning"])
            self.root.after(1000, self.update_timer)
        elif self.timer_running:
            self.timer_running = False
            self.check_answer(timeout=True)

    def check_answer(self, timeout=False):
        self.timer_running = False
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        question_data = self.questions[self.current_question]
        if timeout or self.selected_option.get() == -1:
            result_text, result_color, feedback_text = "Time's Up!", self.colors["warning"], "Pick an answer next time!"
        else:
            correct = self.selected_option.get() == question_data["correct"]
            result_text = "Correct!" if correct else "Wrong!"
            result_color = self.colors["success"] if correct else self.colors["error"]
            feedback_text = question_data["explanation"] if correct else f"Correct: {question_data['options'][question_data['correct']]}\n\n{question_data['explanation']}"
            if correct:
                self.score += 1

        result_label = ttk.Label(self.content_frame, text=result_text, foreground=result_color, font=("Helvetica", 24, "bold"))
        result_label.pack(pady=(70, 20))
        self.fade_in(result_label)

        feedback_label = ttk.Label(self.content_frame, text=feedback_text, style="Feedback.TLabel")
        feedback_label.pack(pady=20)
        self.fade_in(feedback_label)

        next_btn = self.create_modern_button(self.content_frame, "Next", self.next_question)
        next_btn.pack(pady=40)

    def next_question(self):
        self.current_question += 1
        self.display_question() if self.current_question < len(self.questions) else self.show_final_results()

    def show_final_results(self):
        for widget in self.header_frame.winfo_children() + self.content_frame.winfo_children() + self.footer_frame.winfo_children():
            widget.destroy()

        percentage = (self.score / len(self.questions)) * 100
        title_label = ttk.Label(self.content_frame, text="Quiz Done!", style="Title.TLabel")
        title_label.pack(pady=(70, 20))
        self.fade_in(title_label)

        score_label = ttk.Label(self.content_frame, text=f"Score: {self.score}/{len(self.questions)} ({percentage:.1f}%)", font=("Helvetica", 18, "bold"))
        score_label.pack(pady=20)
        self.fade_in(score_label)

        perf_text, perf_color = ("Legendary!", self.colors["success"]) if percentage >= 80 else ("Nice Work!", self.colors["primary"]) if percentage >= 60 else ("Keep Going!", self.colors["warning"])
        perf_label = ttk.Label(self.content_frame, text=perf_text, foreground=perf_color, font=("Helvetica", 14))
        perf_label.pack(pady=20)
        self.fade_in(perf_label)

        button_frame = ttk.Frame(self.content_frame, style="TFrame")
        button_frame.pack(pady=40)
        retry_btn = self.create_modern_button(button_frame, "Retry", self.start_quiz)
        retry_btn.pack(side=tk.LEFT, padx=10)
        new_cat_btn = self.create_modern_button(button_frame, "New Category", self.setup_welcome_screen)
        new_cat_btn.pack(side=tk.LEFT, padx=10)

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = QuizApp(root)
    root.mainloop()