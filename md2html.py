import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import markdown
import os
import webbrowser
from pathlib import Path

class MarkdownToHtmlConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown to HTML Converter")
        self.root.geometry("900x600")
        self.root.configure(bg="#f5f5f5")
        
        # Set up the style
        self.setup_style()
        
        # Set up the UI elements
        self.create_ui()
        
        # Initialize variables
        self.current_file = None
        self.html_output_path = None
        
    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles for buttons, frames, etc.
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TButton', font=('Arial', 10), background='#4a6baf')
        style.configure('TLabel', font=('Arial', 11), background='#f5f5f5')
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background='#f5f5f5')
        
    def create_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="Markdown to HTML Converter", style='Header.TLabel')
        header_label.pack(pady=10)
        
        # Button frame for file operations
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Open file button
        open_button = ttk.Button(button_frame, text="Open Markdown File", command=self.open_file)
        open_button.pack(side=tk.LEFT, padx=5)
        
        # Save HTML button
        save_button = ttk.Button(button_frame, text="Convert & Save HTML", command=self.convert_and_save)
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Preview button
        preview_button = ttk.Button(button_frame, text="Preview in Browser", command=self.preview_html)
        preview_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Paned window for editor and preview
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left frame for markdown editor
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Markdown editor label
        md_label = ttk.Label(left_frame, text="Markdown Editor")
        md_label.pack(anchor='w', pady=(0, 5))
        
        # Markdown editor text area
        self.markdown_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, font=("Consolas", 11))
        self.markdown_text.pack(fill=tk.BOTH, expand=True)
        self.markdown_text.bind("<KeyRelease>", self.update_preview)
        
        # Right frame for HTML preview
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        # HTML preview label
        html_label = ttk.Label(right_frame, text="HTML Preview")
        html_label.pack(anchor='w', pady=(0, 5))
        
        # HTML preview text area
        self.html_preview = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=("Consolas", 11))
        self.html_preview.pack(fill=tk.BOTH, expand=True)
        self.html_preview.config(state=tk.DISABLED)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.markdown_text.delete(1.0, tk.END)
                    self.markdown_text.insert(tk.END, content)
                    self.current_file = file_path
                    self.update_preview()
                    file_name = os.path.basename(file_path)
                    self.status_var.set(f"Opened: {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Error opening file: {str(e)}")
                
    def update_preview(self, event=None):
        markdown_content = self.markdown_text.get(1.0, tk.END)
        html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
        
        # Update HTML preview
        self.html_preview.config(state=tk.NORMAL)
        self.html_preview.delete(1.0, tk.END)
        self.html_preview.insert(tk.END, html_content)
        self.html_preview.config(state=tk.DISABLED)
        
    def convert_and_save(self):
        if not self.markdown_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "Nothing to convert. Please enter some Markdown text.")
            return
            
        initial_dir = os.path.dirname(self.current_file) if self.current_file else os.getcwd()
        initial_file = os.path.basename(os.path.splitext(self.current_file)[0] + ".html") if self.current_file else "untitled.html"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            initialdir=initial_dir,
            initialfile=initial_file
        )
        
        if file_path:
            try:
                markdown_content = self.markdown_text.get(1.0, tk.END)
                html_content = self.generate_full_html(markdown_content)
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(html_content)
                    
                self.html_output_path = file_path
                file_name = os.path.basename(file_path)
                self.status_var.set(f"Saved: {file_name}")
                messagebox.showinfo("Success", f"HTML file saved successfully as {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")
                
    def generate_full_html(self, markdown_content):
        html_body = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
        
        # Create a complete HTML document with basic styling
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Converted Markdown</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 12px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        code {{
            font-family: Consolas, Monaco, "Andale Mono", monospace;
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 4px;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        table, th, td {{
            border: 1px solid #ddd;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            padding-left: 16px;
            margin-left: 0;
            color: #555;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""
        return html_template
    
    def preview_html(self):
        if not self.markdown_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "Nothing to preview. Please enter some Markdown text.")
            return
            
        temp_dir = Path.home() / "temp_markdown_preview"
        temp_dir.mkdir(exist_ok=True)
        temp_file = temp_dir / "preview.html"
        
        try:
            markdown_content = self.markdown_text.get(1.0, tk.END)
            html_content = self.generate_full_html(markdown_content)
            
            with open(temp_file, 'w', encoding='utf-8') as file:
                file.write(html_content)
                
            # Open in default browser
            webbrowser.open(temp_file.as_uri())
            self.status_var.set("Previewing in browser")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating preview: {str(e)}")
    
    def clear(self):
        self.markdown_text.delete(1.0, tk.END)
        self.html_preview.config(state=tk.NORMAL)
        self.html_preview.delete(1.0, tk.END)
        self.html_preview.config(state=tk.DISABLED)
        self.current_file = None
        self.html_output_path = None
        self.status_var.set("Ready")

if __name__ == "__main__":
    # Install required packages if not already installed
    try:
        import markdown
    except ImportError:
        import subprocess
        import sys
        messagebox.showinfo("Installing Dependencies", "Installing required packages. Please wait...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
        import markdown
    
    root = tk.Tk()
    app = MarkdownToHtmlConverter(root)
    root.mainloop()