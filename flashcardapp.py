import tkinter as tk
from tkinter import ttk
import tkinter.simpledialog as simpledialog
import random
import time
import json
import os

class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcard App")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f2f5")

        # Load cards or use defaults
        self.cards = {}
        self.load_cards()
        if not self.cards:
            self.cards = {
                "What is Python?": "A high-level programming language",
                "What is AI?": "Artificial Intelligence",
                "What is 2 + 2?": "4",
                "Capital of France?": "Paris"
            }
        self.card_list = list(self.cards.items())
        self.current_card = 0
        self.showing_answer = False

        # Style configuration
        self.style = ttk.Style()
        self.style.configure("Card.TFrame", 
                           background="#ffffff",
                           relief="raised",
                           borderwidth=2)
        self.style.configure("Button.TButton", 
                           font=('Helvetica', 12),
                           padding=10)

        # Main container
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(expand=True, fill="both")

        # Card frame
        self.card_frame = ttk.Frame(self.main_frame, 
                                  style="Card.TFrame",
                                  width=400, 
                                  height=200)
        self.card_frame.pack(pady=20)
        self.card_frame.pack_propagate(False)

        # Card label
        self.card_label = tk.Label(self.card_frame,
                                 text=self.card_list[self.current_card][0],
                                 font=('Helvetica', 16),
                                 bg="#ffffff",
                                 wraplength=380,
                                 justify="center",
                                 bd=0,
                                 highlightthickness=0,
                                 pady=20)
        self.card_label.pack(expand=True)

        # Buttons frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=20)

        # Buttons
        self.flip_button = ttk.Button(self.button_frame,
                                    text="Flip",
                                    command=self.flip_card,
                                    style="Button.TButton")
        self.flip_button.grid(row=0, column=0, padx=10)

        self.next_button = ttk.Button(self.button_frame,
                                    text="Next",
                                    command=self.next_card,
                                    style="Button.TButton")
        self.next_button.grid(row=0, column=1, padx=10)

        self.add_button = ttk.Button(self.button_frame,
                                   text="Add Card",
                                   command=self.add_card,
                                   style="Button.TButton")
        self.add_button.grid(row=0, column=2, padx=10)

        # Animation variables
        self.animating = False

        # Bind window close to save
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def flip_card(self):
        if not self.animating:
            self.animating = True
            self.showing_answer = not self.showing_answer
            self.animate_flip()

    def animate_flip(self):
        width = 400
        for i in range(0, 101, 10):
            new_width = width * (100 - i) // 100
            if new_width < 0:
                new_width = 0
            self.card_frame.config(width=new_width)
            if i == 50:
                text = self.card_list[self.current_card][1 if self.showing_answer else 0]
                self.card_label.config(text=text)
            self.root.update()
            time.sleep(0.03)
        
        for i in range(0, 101, 10):
            new_width = width * i // 100
            self.card_frame.config(width=new_width)
            self.root.update()
            time.sleep(0.03)
        
        self.animating = False

    def next_card(self):
        if not self.animating:
            self.current_card = (self.current_card + 1) % len(self.card_list)
            self.showing_answer = False
            self.animate_next()

    def animate_next(self):
        self.animating = True
        start_x = 0
        end_x = -600

        for i in range(0, 101, 10):
            x = start_x + (end_x - start_x) * i // 100
            self.card_frame.place(x=x, y=20)
            self.root.update()
            time.sleep(0.02)

        self.card_label.config(text=self.card_list[self.current_card][0])
        self.card_frame.place(x=600, y=20)

        for i in range(0, 101, 10):
            x = 600 + (-600 - 0) * i // 100
            self.card_frame.place(x=x, y=20)
            self.root.update()
            time.sleep(0.02)

        self.card_frame.pack(pady=20)
        self.animating = False

    def add_card(self):
        if not self.animating:
            question = simpledialog.askstring("New Card", "Enter question:", parent=self.root)
            if question:
                answer = simpledialog.askstring("New Card", "Enter answer:", parent=self.root)
                if answer:
                    self.cards[question] = answer
                    self.card_list = list(self.cards.items())
                    self.save_cards()
                    self.current_card = len(self.card_list) - 1
                    self.showing_answer = False
                    self.card_label.config(text=question)

    def save_cards(self):
        with open("flashcards.json", "w") as f:
            json.dump(self.cards, f)

    def load_cards(self):
        try:
            with open("flashcards.json", "r") as f:
                self.cards = json.load(f)
                self.card_list = list(self.cards.items())
        except (FileNotFoundError, json.JSONDecodeError):
            self.cards = {}

    def on_closing(self):
        self.save_cards()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()