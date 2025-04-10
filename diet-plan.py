import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import random

class SmoothButton(tk.Canvas):
    def __init__(self, parent, width, height, text, command=None, bg_color="#6366F1", fg_color="#FFFFFF"):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.text = text
        self.radius = 20
        self.state = "normal"

        self.rect_id = None
        self.text_id = None
        self.draw_button()

        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def draw_button(self):
        if self.rect_id:
            self.delete(self.rect_id)
        if self.text_id:
            self.delete(self.text_id)

        bg = self.bg_color
        if self.state == "hover":
            bg = "#7E8EF1"
        elif self.state == "pressed":
            bg = "#4B56D2"

        self.rect_id = self.create_rounded_rect(0, 0, self.winfo_width(), self.winfo_height(), self.radius, fill=bg)
        self.text_id = self.create_text(
            self.winfo_width()/2, 
            self.winfo_height()/2, 
            text=self.text, 
            fill=self.fg_color, 
            font=("Avenir", 12, "bold")
        )

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_hover(self, event):
        self.state = "hover"
        self.draw_button()

    def on_leave(self, event):
        self.state = "normal"
        self.draw_button()

    def on_press(self, event):
        self.state = "pressed"
        self.draw_button()

    def on_release(self, event):
        self.state = "hover" if self.winfo_containing(event.x_root, event.y_root) == self else "normal"
        self.draw_button()
        if self.command and self.winfo_containing(event.x_root, event.y_root) == self:
            self.command()

class DietApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Diet Flow")
        self.root.geometry("900x650")
        self.root.configure(bg="#F5F7FA")
        
        self.init_db()
        self.setup_ui()

    def init_db(self):
        conn = sqlite3.connect('diet_flow.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY,
            name TEXT,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            food_group TEXT,
            serving TEXT,
            updated TIMESTAMP
        )''')
        
        c.execute("SELECT COUNT(*) FROM foods")
        if c.fetchone()[0] == 0:
            foods = [
                # Protein
                ("Grilled Chicken Breast", 165, 31, 0, 3.6, "Protein", "100g", datetime.now()),
                ("Baked Salmon", 206, 22, 0, 13, "Protein", "100g", datetime.now()),
                ("Greek Yogurt (Non-fat)", 59, 10, 3.6, 0.4, "Protein", "100g", datetime.now()),
                ("Turkey Breast", 135, 30, 0, 1.2, "Protein", "100g", datetime.now()),
                ("Lentils (Cooked)", 116, 9, 20, 0.4, "Protein", "100g", datetime.now()),
                ("Tofu", 76, 8, 1.9, 4.8, "Protein", "100g", datetime.now()),
                ("Egg Whites", 52, 11, 0.7, 0.2, "Protein", "100g", datetime.now()),

                # Grains
                ("Quinoa (Cooked)", 120, 4.4, 21.3, 1.9, "Grains", "100g", datetime.now()),
                ("Brown Rice (Cooked)", 112, 2.6, 23, 0.9, "Grains", "100g", datetime.now()),
                ("Oats (Dry)", 389, 13, 66, 7, "Grains", "100g", datetime.now()),
                ("Sweet Potato (Baked)", 86, 1.6, 20, 0.1, "Grains", "100g", datetime.now()),  # Treated as grain for simplicity
                ("Whole Wheat Pasta (Cooked)", 131, 5.3, 25, 1.1, "Grains", "100g", datetime.now()),

                # Vegetables
                ("Broccoli (Steamed)", 34, 2.8, 7, 0.4, "Vegetables", "100g", datetime.now()),
                ("Spinach (Raw)", 23, 2.9, 3.6, 0.4, "Vegetables", "100g", datetime.now()),
                ("Kale (Raw)", 49, 4.3, 9, 0.9, "Vegetables", "100g", datetime.now()),
                ("Brussels Sprouts (Roasted)", 43, 3.4, 9, 0.3, "Vegetables", "100g", datetime.now()),
                ("Zucchini (Cooked)", 17, 1.2, 3.1, 0.3, "Vegetables", "100g", datetime.now()),

                # Fats
                ("Avocado", 160, 2, 8.5, 14.7, "Fats", "100g", datetime.now()),
                ("Almonds", 579, 21, 22, 49.9, "Fats", "100g", datetime.now()),
                ("Olive Oil", 884, 0, 0, 100, "Fats", "100g", datetime.now()),
                ("Peanut Butter (Natural)", 588, 25, 20, 50, "Fats", "100g", datetime.now()),
                ("Chia Seeds", 486, 17, 42, 31, "Fats", "100g", datetime.now())
            ]
            c.executemany("INSERT INTO foods (name, calories, protein, carbs, fat, food_group, serving, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", foods)
        
        conn.commit()
        conn.close()

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#F5F7FA")
        header.pack(fill="x", pady=20)
        
        tk.Label(header, text="Diet Flow", font=("Avenir", 24, "bold"), bg="#F5F7FA", fg="#2D3748").pack()
        tk.Label(header, text="Your personalized nutrition companion", font=("Avenir", 12), bg="#F5F7FA", fg="#64748B").pack()

        self.content = tk.Frame(self.root, bg="#F5F7FA")
        self.content.pack(fill="both", expand=True, padx=20)

        self.show_input_screen()

    def show_input_screen(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        card = tk.Frame(self.content, bg="#FFFFFF", bd=0)
        card.pack(pady=20, padx=20, fill="both", expand=True)
        card.config(highlightthickness=2, highlightbackground="#E5E7EB", highlightcolor="#E5E7EB")
        
        tk.Label(card, text="Your Profile", font=("Avenir", 18, "bold"), bg="#FFFFFF", fg="#2D3748").pack(pady=(20, 10))
        
        fields_frame = tk.Frame(card, bg="#FFFFFF")
        fields_frame.pack(pady=20, padx=40)

        left_col = tk.Frame(fields_frame, bg="#FFFFFF")
        left_col.pack(side="left", padx=(0, 20))
        
        right_col = tk.Frame(fields_frame, bg="#FFFFFF")
        right_col.pack(side="left")

        self.weight_var = tk.StringVar(value="70")
        tk.Label(left_col, text="Weight (kg)", font=("Avenir", 12), bg="#FFFFFF", fg="#4B5563").pack(anchor="w")
        tk.Entry(left_col, textvariable=self.weight_var, font=("Avenir", 12), bg="#F9FAFB", bd=0).pack(fill="x", pady=5, ipady=5)

        self.height_var = tk.StringVar(value="175")
        tk.Label(left_col, text="Height (cm)", font=("Avenir", 12), bg="#FFFFFF", fg="#4B5563").pack(anchor="w", pady=(10, 0))
        tk.Entry(left_col, textvariable=self.height_var, font=("Avenir", 12), bg="#F9FAFB", bd=0).pack(fill="x", pady=5, ipady=5)

        self.age_var = tk.StringVar(value="30")
        tk.Label(left_col, text="Age", font=("Avenir", 12), bg="#FFFFFF", fg="#4B5563").pack(anchor="w", pady=(10, 0))
        tk.Entry(left_col, textvariable=self.age_var, font=("Avenir", 12), bg="#F9FAFB", bd=0).pack(fill="x", pady=5, ipady=5)

        self.gender_var = tk.StringVar(value="Male")
        tk.Label(right_col, text="Gender", font=("Avenir", 12), bg="#FFFFFF", fg="#4B5563").pack(anchor="w")
        gender_combo = ttk.Combobox(right_col, textvariable=self.gender_var, values=["Male", "Female"], state="readonly", font=("Avenir", 12))
        gender_combo.pack(fill="x", pady=5)
        gender_combo.config(foreground="#4B5563")

        self.activity_var = tk.StringVar(value="Moderately Active")
        tk.Label(right_col, text="Activity Level", font=("Avenir", 12), bg="#FFFFFF", fg="#4B5563").pack(anchor="w", pady=(10, 0))
        activity_combo = ttk.Combobox(right_col, textvariable=self.activity_var, 
                                    values=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"], 
                                    state="readonly", font=("Avenir", 12))
        activity_combo.pack(fill="x", pady=5)
        activity_combo.config(foreground="#4B5563")

        self.goal_var = tk.StringVar(value="Maintain")
        tk.Label(right_col, text="Goal", font=("Avenir", 12), bg="#FFFFFF", fg="#4B5563").pack(anchor="w", pady=(10, 0))
        goal_combo = ttk.Combobox(right_col, textvariable=self.goal_var, 
                                values=["Lose Weight", "Maintain", "Gain Muscle"], 
                                state="readonly", font=("Avenir", 12))
        goal_combo.pack(fill="x", pady=5)
        goal_combo.config(foreground="#4B5563")

        SmoothButton(card, 200, 50, "Generate Plan", self.generate_plan).pack(pady=20)

    def generate_plan(self):
        try:
            weight = float(self.weight_var.get())
            height = float(self.height_var.get())
            age = float(self.age_var.get())
            gender = self.gender_var.get()
            activity = self.activity_var.get()
            goal = self.goal_var.get()

            bmr = (10 * weight) + (6.25 * height) - (5 * age) + (5 if gender == "Male" else -161)
            activity_multipliers = {
                "Sedentary": 1.2,
                "Lightly Active": 1.375,
                "Moderately Active": 1.55,
                "Very Active": 1.725,
                "Extremely Active": 1.9
            }
            tdee = bmr * activity_multipliers[activity]
            calorie_goal = tdee + (-500 if goal == "Lose Weight" else 500 if goal == "Gain Muscle" else 0)

            if goal == "Lose Weight":
                protein_pct, carbs_pct, fat_pct = 0.4, 0.3, 0.3
            elif goal == "Gain Muscle":
                protein_pct, carbs_pct, fat_pct = 0.35, 0.4, 0.25
            else:  # Maintain
                protein_pct, carbs_pct, fat_pct = 0.3, 0.4, 0.3

            protein = (calorie_goal * protein_pct) / 4
            carbs = (calorie_goal * carbs_pct) / 4
            fat = (calorie_goal * fat_pct) / 9

            self.show_results(calorie_goal, protein, carbs, fat)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    def show_results(self, calories, protein, carbs, fat):
        for widget in self.content.winfo_children():
            widget.destroy()

        card = tk.Frame(self.content, bg="#FFFFFF", bd=0)
        card.pack(pady=20, padx=20, fill="both", expand=True)
        card.config(highlightthickness=2, highlightbackground="#E5E7EB", highlightcolor="#E5E7EB")

        tk.Label(card, text="Your Diet Plan", font=("Avenir", 18, "bold"), bg="#FFFFFF", fg="#2D3748").pack(pady=(20, 10))

        macro_frame = tk.Frame(card, bg="#FFFFFF")
        macro_frame.pack(pady=20)

        for label, value, color in [
            ("Calories", f"{int(calories)} kcal", "#6366F1"),
            ("Protein", f"{int(protein)}g", "#10B981"),
            ("Carbs", f"{int(carbs)}g", "#F59E0B"),
            ("Fat", f"{int(fat)}g", "#EF4444")
        ]:
            frame = tk.Frame(macro_frame, bg="#FFFFFF")
            frame.pack(fill="x", pady=5)
            tk.Label(frame, text=label, font=("Avenir", 12), bg="#FFFFFF", fg="#4B5563").pack(side="left")
            tk.Label(frame, text=value, font=("Avenir", 12, "bold"), bg="#FFFFFF", fg=color).pack(side="right")

        meals = self.generate_meals(calories, protein, carbs, fat)
        meal_frame = tk.Canvas(card, bg="#FFFFFF", highlightthickness=0)
        scrollbar = ttk.Scrollbar(card, orient="vertical", command=meal_frame.yview)
        meal_content = tk.Frame(meal_frame, bg="#FFFFFF")
        
        meal_frame.configure(yscrollcommand=scrollbar.set)
        meal_frame.create_window((0, 0), window=meal_content, anchor="nw")
        meal_frame.pack(side="left", fill="both", expand=True, padx=(40, 0))
        scrollbar.pack(side="right", fill="y")

        for meal, items in meals.items():
            meal_card = tk.Frame(meal_content, bg="#F9FAFB", bd=0)
            meal_card.pack(fill="x", pady=5, padx=10)
            meal_card.config(highlightthickness=1, highlightbackground="#E5E7EB")
            
            tk.Label(meal_card, text=meal, font=("Avenir", 14, "bold"), bg="#F9FAFB", fg="#2D3748").pack(anchor="w", pady=5, padx=10)
            
            for item in items:
                tk.Label(meal_card, text=f"{item['name']} ({item['serving']}g) - {int(item['calories'])}kcal, "
                                       f"P: {item['protein']:.1f}g, C: {item['carbs']:.1f}g, F: {item['fat']:.1f}g", 
                        font=("Avenir", 12), bg="#F9FAFB", fg="#4B5563").pack(anchor="w", padx=20)

        meal_content.bind("<Configure>", lambda e: meal_frame.configure(scrollregion=meal_frame.bbox("all")))

        btn_frame = tk.Frame(card, bg="#FFFFFF")
        btn_frame.pack(pady=20)
        SmoothButton(btn_frame, 150, 40, "Back", self.show_input_screen, "#E5E7EB", "#2D3748").pack(side="left", padx=5)
        SmoothButton(btn_frame, 150, 40, "Food Database", self.show_database).pack(side="left", padx=5)

    def generate_meals(self, calories, protein, carbs, fat):
        conn = sqlite3.connect('diet_flow.db')
        c = conn.cursor()
        c.execute("SELECT name, calories, protein, carbs, fat, food_group FROM foods")
        foods = c.fetchall()
        conn.close()

        protein_foods = [f for f in foods if f[5] == "Protein"]
        carb_foods = [f for f in foods if f[5] in ["Grains", "Vegetables"]]
        fat_foods = [f for f in foods if f[5] == "Fats"]

        meals = {
            "Breakfast": {"cal": calories*0.25, "p": protein*0.25, "c": carbs*0.25, "f": fat*0.25},
            "Lunch": {"cal": calories*0.35, "p": protein*0.35, "c": carbs*0.35, "f": fat*0.35},
            "Dinner": {"cal": calories*0.30, "p": protein*0.30, "c": carbs*0.30, "f": fat*0.30},
            "Snack": {"cal": calories*0.10, "p": protein*0.10, "c": carbs*0.10, "f": fat*0.10}
        }

        meal_plan = {}
        for meal, targets in meals.items():
            items = []
            remaining_cal = targets["cal"]
            remaining_p = targets["p"]
            remaining_c = targets["c"]
            remaining_f = targets["f"]

            if protein_foods and remaining_p > 0:
                food = random.choice(protein_foods)
                serving = min(200, max(50, int((remaining_p / food[2]) * 100)))
                cal = (food[1] / 100) * serving
                p = (food[2] / 100) * serving
                c = (food[3] / 100) * serving
                f = (food[4] / 100) * serving
                items.append({"name": food[0], "serving": serving, "calories": cal, "protein": p, "carbs": c, "fat": f})
                remaining_cal -= cal
                remaining_p -= p
                remaining_c -= c
                remaining_f -= f

            if carb_foods and remaining_c > 0 and remaining_cal > 50:
                food = random.choice(carb_foods)
                serving = min(200, max(50, int((remaining_c / food[3]) * 100)))
                cal = (food[1] / 100) * serving
                p = (food[2] / 100) * serving
                c = (food[3] / 100) * serving
                f = (food[4] / 100) * serving
                items.append({"name": food[0], "serving": serving, "calories": cal, "protein": p, "carbs": c, "fat": f})
                remaining_cal -= cal
                remaining_p -= p
                remaining_c -= c
                remaining_f -= f

            if fat_foods and remaining_f > 0 and remaining_cal > 50 and meal != "Snack":
                food = random.choice(fat_foods)
                serving = min(50, max(10, int((remaining_f / food[4]) * 100)))
                cal = (food[1] / 100) * serving
                p = (food[2] / 100) * serving
                c = (food[3] / 100) * serving
                f = (food[4] / 100) * serving
                items.append({"name": food[0], "serving": serving, "calories": cal, "protein": p, "carbs": c, "fat": f})

            meal_plan[meal] = items

        return meal_plan

    def show_database(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        card = tk.Frame(self.content, bg="#FFFFFF", bd=0)
        card.pack(pady=20, padx=20, fill="both", expand=True)
        card.config(highlightthickness=2, highlightbackground="#E5E7EB", highlightcolor="#E5E7EB")

        tk.Label(card, text="Food Database", font=("Avenir", 18, "bold"), bg="#FFFFFF", fg="#2D3748").pack(pady=(20, 10))

        tree = ttk.Treeview(card, columns=("name", "cal", "pro", "carb", "fat"), show="headings")
        tree.heading("name", text="Name")
        tree.heading("cal", text="Cal (100g)")
        tree.heading("pro", text="Protein (g)")
        tree.heading("carb", text="Carbs (g)")
        tree.heading("fat", text="Fat (g)")
        tree.pack(fill="both", expand=True, padx=40, pady=10)

        conn = sqlite3.connect('diet_flow.db')
        c = conn.cursor()
        c.execute("SELECT name, calories, protein, carbs, fat FROM foods")
        for row in c.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

        btn_frame = tk.Frame(card, bg="#FFFFFF")
        btn_frame.pack(pady=20)
        SmoothButton(btn_frame, 150, 40, "Back", self.show_results, "#E5E7EB", "#2D3748").pack(side="left", padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = DietApp(root)
    root.mainloop()