import tkinter as tk
from tkinter import ttk
import pygame
import numpy as np
import random

# Initialize Pygame mixer for sound (stereo, 2 channels)
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Frequencies for Sargam notes
NOTE_FREQUENCIES = {
    'Sa': 261.63, 'Re': 294.33, 'Ga': 327.03, 'Ma': 348.83,
    'Pa': 392.44, 'Dha': 436.05, 'Ni': 490.55, 'Sa2': 523.25
}

# Generate a sine wave sound
def generate_tone(frequency, duration=0.5, volume=0.5):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    tone = np.sin(frequency * t * 2 * np.pi)
    sound = (tone * volume * 32767).astype(np.int16)
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Pre-generate sounds
sounds = {note: generate_tone(NOTE_FREQUENCIES[note]) for note in NOTE_FREQUENCIES}

# Main application class
class PianoLessonsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sargam Lessons")
        self.root.geometry("900x450")
        self.root.resizable(False, False)

        # Gradient background
        self.bg_canvas = tk.Canvas(self.root, width=900, height=450, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.bg_canvas.create_rectangle(0, 0, 900, 450, fill="#1e1e2f", outline="")
        self.bg_canvas.create_rectangle(0, 0, 900, 225, fill="#2a2a40", outline="")

        # Lesson data
        self.follow_sequence = ['Sa', 'Re', 'Ga', 'Ma', 'Pa', 'Dha', 'Ni', 'Sa2', 'Ni', 'Dha', 'Pa', 'Ma', 'Ga', 'Re', 'Sa']
        self.current_step = 0
        self.current_mode = "follow"  # "follow" or "predict"
        self.current_predict_note = None
        self.score = 0
        self.attempts = 0

        # UI elements
        self.keys = {}
        self.create_keys()
        self.create_labels()
        self.create_mode_buttons()

        # Start in Follow Mode
        self.start_lesson()

        # Bind window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_keys(self):
        key_frame = tk.Frame(self.bg_canvas, bg="#2a2a40")
        self.bg_canvas.create_window(450, 350, window=key_frame)
        notes = ['Sa', 'Re', 'Ga', 'Ma', 'Pa', 'Dha', 'Ni', 'Sa2']

        for i, note in enumerate(notes):
            key = tk.Button(key_frame, text=note, font=("Helvetica", 16, "bold"), bg="#ffffff", fg="#333333",
                            width=8, height=3, relief="flat", bd=0, activebackground="#d3d3d3",
                            command=lambda n=note: self.play_note(n))
            key.grid(row=0, column=i, padx=5, pady=10)
            key.config(highlightbackground="#2a2a40", highlightthickness=2)
            self.keys[note] = key

    def create_labels(self):
        self.lesson_label = tk.Label(self.bg_canvas, text="Follow the highlighted note!", font=("Helvetica", 20, "bold"),
                                     bg="#2a2a40", fg="#ffffff", pady=10)
        self.bg_canvas.create_window(450, 50, window=self.lesson_label)

        self.feedback_label = tk.Label(self.bg_canvas, text="", font=("Helvetica", 14), bg="#2a2a40", fg="#ffffff")
        self.bg_canvas.create_window(450, 100, window=self.feedback_label)

        self.score_label = tk.Label(self.bg_canvas, text="Score: 0/0", font=("Helvetica", 14), bg="#2a2a40", fg="#ffffff")
        self.bg_canvas.create_window(450, 150, window=self.score_label)

    def create_mode_buttons(self):
        mode_frame = tk.Frame(self.bg_canvas, bg="#2a2a40")
        self.bg_canvas.create_window(450, 200, window=mode_frame)

        follow_btn = tk.Button(mode_frame, text="Follow Mode", font=("Helvetica", 12), bg="#4a4a6a", fg="#ffffff",
                               relief="flat", command=self.switch_to_follow)
        follow_btn.grid(row=0, column=0, padx=10, pady=5)

        predict_btn = tk.Button(mode_frame, text="Predict Mode", font=("Helvetica", 12), bg="#4a4a6a", fg="#ffffff",
                                relief="flat", command=self.switch_to_predict)
        predict_btn.grid(row=0, column=1, padx=10, pady=5)

    def switch_to_follow(self):
        self.current_mode = "follow"
        self.current_step = 0
        self.score = 0
        self.attempts = 0
        self.update_score()
        self.start_lesson()

    def switch_to_predict(self):
        self.current_mode = "predict"
        self.score = 0
        self.attempts = 0
        self.update_score()
        self.start_lesson()

    def start_lesson(self):
        for key in self.keys.values():
            key.config(state="normal", bg="#ffffff")  # Reset keys

        if self.current_mode == "follow":
            if self.current_step < len(self.follow_sequence):
                target_note = self.follow_sequence[self.current_step]
                self.highlight_note(target_note)
                self.lesson_label.config(text=f"Play: {target_note}")
            else:
                self.lesson_label.config(text="Follow Mode Complete!")
                for key in self.keys.values():
                    key.config(state="disabled")
        elif self.current_mode == "predict":
            self.current_predict_note = random.choice(list(NOTE_FREQUENCIES.keys()))
            sounds[self.current_predict_note].play()
            self.lesson_label.config(text="Listen and guess the note!")
            self.feedback_label.config(text="Click a note to guess", fg="#ffffff")

    def highlight_note(self, note):
        for n, key in self.keys.items():
            key.config(bg="#ffffff" if n != note else "#ffd700")

    def play_note(self, note):
        sounds[note].play()
        self.animate_key(note)

        if self.current_mode == "follow":
            target_note = self.follow_sequence[self.current_step]
            if note == target_note:
                self.feedback_label.config(text="Correct!", fg="#00ff00")
                self.current_step += 1
                self.root.after(500, self.start_lesson)
            else:
                self.feedback_label.config(text="Try Again!", fg="#ff0000")
        elif self.current_mode == "predict":
            self.attempts += 1
            if note == self.current_predict_note:
                self.score += 1
                self.feedback_label.config(text=f"Correct! It was {note}", fg="#00ff00")
                self.update_score()
                self.root.after(1000, self.start_lesson)  # Next note after delay
            else:
                self.feedback_label.config(text=f"Wrong! It was {self.current_predict_note}. Try again?", fg="#ff0000")
                self.update_score()
                self.root.after(1000, lambda: sounds[self.current_predict_note].play())  # Replay note

    def animate_key(self, note):
        key = self.keys[note]
        original_bg = key.cget("bg")
        key.config(bg="#d3d3d3")
        self.root.after(100, lambda: key.config(bg=original_bg))

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}/{self.attempts}")

    def on_closing(self):
        pygame.mixer.quit()
        self.root.destroy()

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = PianoLessonsApp(root)
    root.mainloop()