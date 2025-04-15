import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from PIL import Image, ImageGrab
import math

class MSPaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MS Paint Modern")
        self.root.geometry("900x650")
        self.root.configure(bg="#ffffff")  # White base

        # Variables
        self.drawing = False
        self.last_x = None
        self.last_y = None
        self.tool = "pencil"
        self.brush_size = 2
        self.color = "#000000"
        self.history = []
        self.redo_stack = []
        self.points = []  # For polygon

        # Main frame
        main_frame = tk.Frame(self.root, bg="#ffffff")
        main_frame.pack(fill="both", expand=True)

        # Top bar (actions)
        top_bar = tk.Frame(main_frame, bg="#f7f7f7", relief="flat")
        top_bar.pack(fill="x", pady=(0, 1))

        style = ttk.Style()
        style.configure("Modern.TButton", font=("Segoe UI", 10, "bold"), padding=8, background="#f7f7f7", foreground="#333333")
        style.map("Modern.TButton", background=[("active", "#e0e0e0")])

        ttk.Button(top_bar, text="Undo", command=self.undo, style="Modern.TButton").pack(side="left", padx=5)
        ttk.Button(top_bar, text="Redo", command=self.redo, style="Modern.TButton").pack(side="left", padx=5)
        ttk.Button(top_bar, text="Clear", command=self.clear_canvas, style="Modern.TButton").pack(side="left", padx=5)
        ttk.Button(top_bar, text="Save", command=self.save_image, style="Modern.TButton").pack(side="left", padx=5)

        # Sidebar (tools)
        sidebar = tk.Frame(main_frame, bg="#f0f0f0", width=100)
        sidebar.pack(side="left", fill="y", padx=(0, 1))

        tools = [
            ("Pencil", "pencil"),
            ("Eraser", "eraser"),
            ("Fill", "fill"),
            ("Line", "line"),
            ("Rect", "rectangle"),
            ("Oval", "oval"),
            ("Poly", "polygon")
        ]
        for text, tool in tools:
            btn = ttk.Button(sidebar, text=text, command=lambda t=tool: self.set_tool(t), style="Modern.TButton", width=10)
            btn.pack(pady=5, padx=5)

        # Brush size
        tk.Label(sidebar, text="Size", bg="#f0f0f0", fg="#333333", font=("Segoe UI", 10)).pack(pady=(10, 0))
        self.size_var = tk.IntVar(value=2)
        size_menu = tk.OptionMenu(sidebar, self.size_var, 1, 2, 4, 8, 16, command=self.set_brush_size)
        size_menu.config(bg="#ffffff", font=("Segoe UI", 10), relief="flat", highlightthickness=0)
        size_menu.pack(pady=5, padx=5)

        # Color picker
        ttk.Button(sidebar, text="Color", command=self.choose_color, style="Modern.TButton", width=10).pack(pady=5, padx=5)
        self.color_preview = tk.Label(sidebar, bg=self.color, width=4, height=2, relief="flat", bd=1)
        self.color_preview.pack(pady=5)

        # Canvas
        canvas_frame = tk.Frame(main_frame, bg="#ffffff")
        canvas_frame.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_frame, bg="white", width=750, height=550, highlightthickness=0, bd=1, relief="solid")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

        # Status bar
        self.status_var = tk.StringVar(value="Tool: Pencil | Size: 2 | Color: #000000")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, bg="#f7f7f7", fg="#666666", font=("Segoe UI", 9), anchor="w", relief="flat")
        status_bar.pack(fill="x", side="bottom")

    def set_tool(self, tool):
        self.tool = tool
        if tool == "polygon":
            self.points = []
        self.update_status()

    def set_brush_size(self, size):
        self.brush_size = size
        self.update_status()

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Color")[1]
        if color:
            self.color = color
            self.color_preview.config(bg=color)
            self.update_status()

    def update_status(self):
        self.status_var.set(f"Tool: {self.tool.capitalize()} | Size: {self.brush_size} | Color: {self.color}")

    def start_drawing(self, event):
        self.drawing = True
        self.last_x, self.last_y = event.x, event.y
        if self.tool in ["line", "rectangle", "oval", "polygon"]:
            self.temp_shape = None
        if self.tool == "polygon":
            self.points.append((event.x, event.y))
            self.canvas.create_oval(event.x-2, event.y-2, event.x+2, event.y+2, fill="red")

    def draw(self, event):
        if not self.drawing:
            return
        current_x, current_y = event.x, event.y

        if self.tool == "pencil":
            shape = self.canvas.create_line(self.last_x, self.last_y, current_x, current_y, fill=self.color, width=self.brush_size, capstyle="round")
            self.history.append(shape)
            self.redo_stack.clear()
            self.last_x, self.last_y = current_x, current_y

        elif self.tool == "eraser":
            shape = self.canvas.create_line(self.last_x, self.last_y, current_x, current_y, fill="white", width=self.brush_size * 2, capstyle="round")
            self.history.append(shape)
            self.redo_stack.clear()
            self.last_x, self.last_y = current_x, current_y

        elif self.tool in ["line", "rectangle", "oval", "polygon"]:
            if self.temp_shape:
                self.canvas.delete(self.temp_shape)
            if self.tool == "line":
                self.temp_shape = self.canvas.create_line(self.last_x, self.last_y, current_x, current_y, fill=self.color, width=self.brush_size)
            elif self.tool == "rectangle":
                self.temp_shape = self.canvas.create_rectangle(self.last_x, self.last_y, current_x, current_y, outline=self.color, width=self.brush_size)
            elif self.tool == "oval":
                self.temp_shape = self.canvas.create_oval(self.last_x, self.last_y, current_x, current_y, outline=self.color, width=self.brush_size)
            elif self.tool == "polygon" and len(self.points) > 1:
                self.temp_shape = self.canvas.create_line(self.points[-1], (current_x, current_y), fill=self.color, width=self.brush_size, dash=(2, 2))

    def stop_drawing(self, event):
        if self.drawing:
            current_x, current_y = event.x, event.y
            if self.tool in ["line", "rectangle", "oval"]:
                self.canvas.delete(self.temp_shape)
                if self.tool == "line":
                    shape = self.canvas.create_line(self.last_x, self.last_y, current_x, current_y, fill=self.color, width=self.brush_size)
                elif self.tool == "rectangle":
                    shape = self.canvas.create_rectangle(self.last_x, self.last_y, current_x, current_y, outline=self.color, width=self.brush_size)
                elif self.tool == "oval":
                    shape = self.canvas.create_oval(self.last_x, self.last_y, current_x, current_y, outline=self.color, width=self.brush_size)
                self.history.append(shape)
                self.redo_stack.clear()
            elif self.tool == "polygon" and len(self.points) >= 3:
                if abs(current_x - self.points[0][0]) < 10 and abs(current_y - self.points[0][1]) < 10:
                    shape = self.canvas.create_polygon(self.points, fill=self.color, outline="black", width=self.brush_size)
                    self.history.append(shape)
                    self.redo_stack.clear()
                    self.points = []
            elif self.tool == "fill":
                self.flood_fill(event.x, event.y, self.color)
            self.drawing = False
            self.temp_shape = None

    def flood_fill(self, x, y, fill_color):
        target_color = "#ffffff"
        if self.canvas.coords(self.canvas.find_closest(x, y)):
            items = self.canvas.find_overlapping(x, y, x+1, y+1)
            if items and self.canvas.itemcget(items[0], "fill") == target_color:
                shape = self.canvas.create_rectangle(x, y, x+1, y+1, fill=fill_color, outline=fill_color)
                self.history.append(shape)
                self.redo_stack.clear()
                self.flood_fill(x+1, y, fill_color)
                self.flood_fill(x-1, y, fill_color)
                self.flood_fill(x, y+1, fill_color)
                self.flood_fill(x, y-1, fill_color)

    def undo(self):
        if self.history:
            item = self.history.pop()
            self.redo_stack.append(item)
            self.canvas.delete(item)
            self.update_status()

    def redo(self):
        if self.redo_stack:
            item = self.redo_stack.pop()
            self.history.append(item)
            coords = self.canvas.coords(item)
            if coords:
                self.canvas.create_line(coords, fill=self.color, width=self.brush_size)
            self.update_status()

    def clear_canvas(self):
        def fade_out(step=1.0):
            if step > 0:
                self.canvas.configure(bg=f"#{int(255*step):02x}{int(255*step):02x}{int(255*step):02x}")
                self.root.after(20, fade_out, step - 0.1)
            else:
                self.canvas.delete("all")
                self.canvas.configure(bg="white")
                self.history.clear()
                self.redo_stack.clear()
                self.points = []
                self.update_status()
        fade_out()

    def save_image(self):
        try:
            x = self.root.winfo_rootx() + self.canvas.winfo_x()
            y = self.root.winfo_rooty() + self.canvas.winfo_y()
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height()
            ImageGrab.grab().crop((x, y, x1, y1)).save("painting.png", "PNG")
            messagebox.showinfo("Saved", "Image saved as 'painting.png'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MSPaintApp(root)
    root.mainloop()