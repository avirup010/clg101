import tkinter as tk
from tkinter import ttk, colorchooser
from ttkthemes import ThemedTk
import math

class AnimatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Animator")
        self.root.geometry("800x600")
        self.root.configure(bg="#e6f0fa")  # Soft blue background

        # Variables
        self.points = []
        self.point_ids = []
        self.shape = None
        self.running = False
        self.x_speed = 2
        self.y_speed = 0
        self.rotation = 0
        self.fill_color = "#4a90e2"  # Bright blue default

        # Status bar (initialize early)
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w", background="#d9e6f2", foreground="#2c3e50")
        status_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        # Main frame
        main_frame = ttk.Frame(self.root, style="Main.TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Toolbar
        toolbar = ttk.Frame(main_frame, style="Toolbar.TFrame")
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")

        btn_style = ttk.Style()
        btn_style.configure("Modern.TButton", font=("Helvetica", 10, "bold"), padding=6, background="#ffffff")
        btn_style.map("Modern.TButton", background=[("active", "#d9e6f2")])

        ttk.Button(toolbar, text="Undo", command=self.undo_point, style="Modern.TButton").grid(row=0, column=0, padx=2)
        ttk.Button(toolbar, text="Clear Canvas", command=self.clear_canvas, style="Modern.TButton").grid(row=0, column=1, padx=2)

        # Canvas
        self.canvas = tk.Canvas(main_frame, width=600, height=450, bg="white", highlightthickness=1, highlightbackground="#b3cde0")
        self.canvas.grid(row=1, column=1, sticky="nsew", padx=(0, 5), pady=5)
        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<B1-Motion>", self.preview_shape)

        # Sidebar for tools
        sidebar = ttk.Frame(main_frame, style="Sidebar.TFrame")
        sidebar.grid(row=1, column=0, sticky="ns", padx=5, pady=5)

        ttk.Label(sidebar, text="Tools", font=("Helvetica", 14, "bold"), foreground="#2c3e50").pack(pady=(0, 10))
        ttk.Button(sidebar, text="Finish Shape", command=self.create_shape, style="Modern.TButton").pack(fill="x", pady=2)
        ttk.Button(sidebar, text="Start Animation", command=self.start_animation, style="Modern.TButton").pack(fill="x", pady=2)
        ttk.Button(sidebar, text="Stop Animation", command=self.stop_animation, style="Modern.TButton").pack(fill="x", pady=2)
        ttk.Button(sidebar, text="Pick Color", command=self.choose_color, style="Modern.TButton").pack(fill="x", pady=2)

        # Control panel
        control_panel = ttk.LabelFrame(main_frame, text="Animation Controls", padding=10, style="Control.TLabelframe")
        control_panel.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)

        ttk.Label(control_panel, text="X Speed:", foreground="#34495e").grid(row=0, column=0, padx=5, pady=5)
        self.x_speed_slider = ttk.Scale(control_panel, from_=-5, to=5, orient="horizontal", command=self.update_x_speed)
        self.x_speed_slider.set(2)
        self.x_speed_slider.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(control_panel, text="Y Speed:", foreground="#34495e").grid(row=1, column=0, padx=5, pady=5)
        self.y_speed_slider = ttk.Scale(control_panel, from_=-5, to=5, orient="horizontal", command=self.update_y_speed)
        self.y_speed_slider.set(0)
        self.y_speed_slider.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(control_panel, text="Rotation:", foreground="#34495e").grid(row=2, column=0, padx=5, pady=5)
        self.rot_slider = ttk.Scale(control_panel, from_=-5, to=5, orient="horizontal", command=self.update_rotation)
        self.rot_slider.set(0)
        self.rot_slider.grid(row=2, column=1, padx=5, pady=5)

        # Grid weights for main_frame
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Custom styles
        style = ttk.Style()
        style.configure("Main.TFrame", background="#e6f0fa")
        style.configure("Toolbar.TFrame", background="#ffffff", relief="flat")
        style.configure("Sidebar.TFrame", background="#ffffff", relief="flat")
        style.configure("Control.TLabelframe", background="#ffffff")

    def add_point(self, event):
        if not self.shape:
            x, y = event.x, event.y
            self.points.append((x, y))
            point_id = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="#e74c3c")
            self.point_ids.append(point_id)
            self.status_var.set(f"Point added at ({x}, {y})")

    def undo_point(self):
        if self.points and not self.shape:
            self.points.pop()
            self.canvas.delete(self.point_ids.pop())
            self.canvas.delete("preview")
            self.status_var.set("Last point undone")

    def preview_shape(self, event):
        if self.points and not self.shape:
            self.canvas.delete("preview")
            x, y = event.x, event.y
            preview_points = self.points + [(x, y)]
            self.canvas.create_line(preview_points + [self.points[0]], fill="#95a5a6", dash=(2, 2), tags="preview")

    def create_shape(self):
        if len(self.points) >= 3 and not self.shape:
            self.canvas.delete("preview")
            self.shape = self.canvas.create_polygon(self.points, fill=self.fill_color, outline="black")
            self.points = []
            self.point_ids = []
            self.status_var.set("Shape created")

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Shape Color")[1]
        if color and self.shape:
            self.fill_color = color
            self.canvas.itemconfig(self.shape, fill=color)
            self.status_var.set(f"Color changed to {color}")

    def update_x_speed(self, value):
        self.x_speed = float(value)
        self.status_var.set(f"X Speed: {self.x_speed:.1f}")

    def update_y_speed(self, value):
        self.y_speed = float(value)
        self.status_var.set(f"Y Speed: {self.y_speed:.1f}")

    def update_rotation(self, value):
        self.rotation = float(value)
        self.status_var.set(f"Rotation: {self.rotation:.1f}°")

    def animate(self):
        if self.running and self.shape:
            self.canvas.move(self.shape, self.x_speed, self.y_speed)
            coords = self.canvas.coords(self.shape)
            x_coords = coords[::2]
            y_coords = coords[1::2]
            min_x, max_x = min(x_coords), max(x_coords)
            min_y, max_y = min(y_coords), max(y_coords)

            if max_x >= 600 or min_x <= 0:
                self.x_speed = -self.x_speed * 0.9
                self.x_speed_slider.set(self.x_speed)
            if max_y >= 450 or min_y <= 0:
                self.y_speed = -self.y_speed * 0.9
                self.y_speed_slider.set(self.y_speed)

            if self.rotation != 0:
                center_x = sum(x_coords) / len(x_coords)
                center_y = sum(y_coords) / len(y_coords)
                new_coords = []
                angle = math.radians(self.rotation)
                for i in range(0, len(coords), 2):
                    x, y = coords[i], coords[i+1]
                    x -= center_x
                    y -= center_y
                    new_x = x * math.cos(angle) - y * math.sin(angle)
                    new_y = x * math.sin(angle) + y * math.cos(angle)
                    new_coords.extend([new_x + center_x, new_y + center_y])
                self.canvas.coords(self.shape, *new_coords)

            self.root.after(20, self.animate)
            self.status_var.set("Animating...")

    def start_animation(self):
        if not self.running and self.shape:
            self.running = True
            self.animate()

    def stop_animation(self):
        self.running = False
        self.status_var.set("Animation stopped")

    def clear_canvas(self):
        self.running = False
        self.canvas.delete("all")
        self.points = []
        self.point_ids = []
        self.shape = None
        self.x_speed_slider.set(2)
        self.y_speed_slider.set(0)
        self.rot_slider.set(0)
        self.x_speed, self.y_speed, self.rotation = 2, 0, 0
        self.status_var.set("Canvas cleared")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = AnimatorApp(root)
    root.mainloop()