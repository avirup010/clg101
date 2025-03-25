import tkinter as tk
from tkinter import ttk, filedialog
import re
from PyPDF2 import PdfReader
import time
from PIL import Image, ImageTk
import os

# Industry-standard ATS scoring logic
def calculate_ats_score(resume_text):
    resume_text = resume_text.lower()
    word_count = len(resume_text.split())
    
    common_keywords = [
        "experience", "skills", "education", "team", "project", "management",
        "communication", "problem-solving", "leadership", "development",
        "certification", "training", "software", "results", "achievement"
    ]
    
    keyword_matches = sum(1 for kw in common_keywords if kw in resume_text)
    length_score = min(word_count / 200, 1.0)
    formatting_score = 1.0 if bool(re.search(r'[•\-\*]', resume_text)) else 0.5
    contact_info_score = 1.0 if bool(re.search(r'(email|phone|\b\w+@\w+\.\w+\b)', resume_text)) else 0.5
    
    keyword_weight = 0.4
    length_weight = 0.2
    format_weight = 0.2
    contact_weight = 0.2
    
    score = (keyword_matches / len(common_keywords) * keyword_weight +
             length_score * length_weight +
             formatting_score * format_weight +
             contact_info_score * contact_weight) * 100
    
    return min(round(score, 1), 100.0)

# Extract text from file
def extract_text_from_file(file_path):
    if file_path.endswith(".pdf"):
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    elif file_path.endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            return f"Error reading TXT: {str(e)}"
    return "Unsupported file format. Please upload a .txt or .pdf file."

# Animation for score display with color transition
def animate_score(canvas, text_id, gauge_id, target_score, current_score=0, step=1):
    if current_score < target_score:
        current_score += step
        green = int(min(current_score * 2.55, 255))
        red = int(max(255 - current_score * 2.55, 0))
        color = f"#{red:02x}{green:02x}00"
        canvas.itemconfig(text_id, text=f"{current_score}%", fill=color)
        # Animate gauge arc
        extent = (current_score / 100) * 360
        canvas.itemconfig(gauge_id, extent=extent)
        canvas.after(20, animate_score, canvas, text_id, gauge_id, target_score, current_score, step)
    else:
        final_color = "#00FF00" if target_score > 70 else "#FFA500" if target_score > 40 else "#FF0000"
        canvas.itemconfig(text_id, text=f"{target_score}%", fill=final_color)
        canvas.itemconfig(gauge_id, extent=(target_score / 100) * 360)

# Main Application
class ATSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ATS Resume Analyzer")
        
        # Set to maximum screen resolution
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

        # Theme settings
        self.themes = {
            "dark": {"bg": "#1A1A2E", "card": "#16213E", "text": "#E0E0E0", "accent": "#0F3460", "button": "#E94560"},
            "light": {"bg": "#F0F4F8", "card": "#FFFFFF", "text": "#333333", "accent": "#D3E0EA", "button": "#4A90E2"}
        }
        self.current_theme = "dark"
        self.root.configure(bg=self.themes[self.current_theme]["bg"])

        # Main canvas
        self.canvas = tk.Canvas(root, width=self.screen_width, height=self.screen_height, highlightthickness=0,
                               bg=self.themes[self.current_theme]["bg"])
        self.canvas.pack(fill="both", expand=True)

        # Pill-shaped card
        card_width, card_height = int(self.screen_width * 0.5), int(self.screen_height * 0.6)
        self.card_x, self.card_y = (self.screen_width - card_width) // 2, (self.screen_height - card_height) // 2
        self.create_pill_shape(self.card_x, self.card_y, card_width, card_height, self.themes[self.current_theme]["card"])

        # Title
        self.title_id = self.canvas.create_text(self.screen_width // 2, self.card_y + 70,
                                               text="ATS Resume Analyzer",
                                               font=("Poppins", 36, "bold"), fill=self.themes[self.current_theme]["text"],
                                               anchor="center")

        # Theme Toggle Button
        self.theme_button = ttk.Button(root, text="☀️ Light", command=self.toggle_theme, style="Theme.TButton")
        self.theme_button.place(x=self.card_x + card_width - 100, y=self.card_y + 20, width=80, height=40)

        # Upload Button
        self.upload_button = ttk.Button(root, text="Upload Resume", command=self.upload_file, style="Modern.TButton")
        self.upload_button.place(x=self.screen_width // 2 - 100, y=self.card_y + 150, width=200, height=60)

        # File Label
        self.file_text_id = self.canvas.create_text(self.screen_width // 2, self.card_y + 250,
                                                   text="Upload a PDF or TXT file",
                                                   font=("Poppins", 16), fill=self.themes[self.current_theme]["text"],
                                                   anchor="center")

        # Score Display with circular gauge
        self.gauge_id = self.canvas.create_arc(self.screen_width // 2 - 100, self.card_y + 320,
                                              self.screen_width // 2 + 100, self.card_y + 520,
                                              start=90, extent=0, style="arc", outline=self.themes[self.current_theme]["button"],
                                              width=10)
        self.score_text_id = self.canvas.create_text(self.screen_width // 2, self.card_y + 420,
                                                    text="0%", font=("Poppins", 48, "bold"),
                                                    fill=self.themes[self.current_theme]["text"], anchor="center")

        # Style configuration
        self.style = ttk.Style()
        self.update_styles()

        # Hover animations
        self.upload_button.bind("<Enter>", lambda e: self.upload_button.config(style="Hover.TButton"))
        self.upload_button.bind("<Leave>", lambda e: self.upload_button.config(style="Modern.TButton"))

        self.file_path = None

    def create_pill_shape(self, x, y, width, height, fill):
        radius = height // 2
        self.canvas.create_oval(x, y, x + 2 * radius, y + 2 * radius, fill=fill, outline="")
        self.canvas.create_oval(x + width - 2 * radius, y, x + width, y + 2 * radius, fill=fill, outline="")
        self.canvas.create_rectangle(x + radius, y, x + width - radius, y + height, fill=fill, outline="")

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.theme_button.config(text="🌙 Dark" if self.current_theme == "light" else "☀️ Light")
        self.root.configure(bg=self.themes[self.current_theme]["bg"])
        self.canvas.configure(bg=self.themes[self.current_theme]["bg"])
        self.canvas.delete("all")
        self.create_pill_shape(self.card_x, self.card_y, int(self.screen_width * 0.5), int(self.screen_height * 0.6),
                              self.themes[self.current_theme]["card"])
        self.title_id = self.canvas.create_text(self.screen_width // 2, self.card_y + 70, text="ATS Resume Analyzer",
                                               font=("Poppins", 36, "bold"), fill=self.themes[self.current_theme]["text"],
                                               anchor="center")
        self.file_text_id = self.canvas.create_text(self.screen_width // 2, self.card_y + 250,
                                                   text="Upload a PDF or TXT file" if not self.file_path else self.file_path.split('/')[-1],
                                                   font=("Poppins", 16), fill=self.themes[self.current_theme]["text"],
                                                   anchor="center")
        self.gauge_id = self.canvas.create_arc(self.screen_width // 2 - 100, self.card_y + 320,
                                              self.screen_width // 2 + 100, self.card_y + 520,
                                              start=90, extent=0, style="arc", outline=self.themes[self.current_theme]["button"],
                                              width=10)
        self.score_text_id = self.canvas.create_text(self.screen_width // 2, self.card_y + 420,
                                                    text="0%", font=("Poppins", 48, "bold"),
                                                    fill=self.themes[self.current_theme]["text"], anchor="center")
        self.update_styles()
        self.theme_button.place(x=self.card_x + int(self.screen_width * 0.5) - 100, y=self.card_y + 20)
        self.upload_button.place(x=self.screen_width // 2 - 100, y=self.card_y + 150)

    def update_styles(self):
        self.style.configure("Modern.TButton", font=("Poppins", 14, "bold"), padding=10,
                            background=self.themes[self.current_theme]["button"], foreground="#FFFFFF",
                            borderwidth=0, relief="flat")
        self.style.map("Modern.TButton", background=[("active", "#D32F49" if self.current_theme == "dark" else "#357ABD")])
        self.style.configure("Hover.TButton", background="#D32F49" if self.current_theme == "dark" else "#357ABD")
        self.style.configure("Theme.TButton", font=("Poppins", 12), padding=5,
                            background=self.themes[self.current_theme]["accent"], foreground=self.themes[self.current_theme]["text"])

    def upload_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt")])
        if self.file_path:
            self.canvas.itemconfig(self.file_text_id, text=f"{self.file_path.split('/')[-1]}",
                                 fill=self.themes[self.current_theme]["text"])
            self.calculate_score()
        else:
            self.canvas.itemconfig(self.file_text_id, text="Upload a PDF or TXT file",
                                 fill=self.themes[self.current_theme]["text"])

    def calculate_score(self):
        if not self.file_path:
            self.canvas.itemconfig(self.score_text_id, text="Upload First!", fill="#FF4444")
            return
        
        resume_text = extract_text_from_file(self.file_path)
        if "Error" in resume_text:
            self.canvas.itemconfig(self.score_text_id, text="Error!", fill="#FF4444")
            self.canvas.itemconfig(self.file_text_id, text=resume_text, fill="#FF4444")
            return
        
        score = calculate_ats_score(resume_text)
        self.canvas.itemconfig(self.score_text_id, text="0%", fill=self.themes[self.current_theme]["text"])
        self.canvas.itemconfig(self.gauge_id, extent=0)
        animate_score(self.canvas, self.score_text_id, self.gauge_id, score)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    # Use Poppins font (install it or fallback to Helvetica)
    try:
        root.option_add("*Font", "Poppins")
    except:
        root.option_add("*Font", "Helvetica")
    app = ATSApp(root)
    root.mainloop()
