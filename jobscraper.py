import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import threading
from PIL import Image, ImageTk
import time
import webbrowser

class JobScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JobScraper Pro")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f2f5")
        
        # Initialize is_scraping here
        self.is_scraping = False
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom styles
        self.style.configure("Custom.TButton", 
                            font=('Helvetica', 12, 'bold'),
                            padding=10,
                            background="#4a90e2",
                            foreground="white")
        self.style.map("Custom.TButton",
                      background=[('active', '#357abd')])

        self.create_gui()

    def create_gui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#4a90e2", pady=20)
        header_frame.pack(fill="x")
        
        title_label = tk.Label(header_frame, 
                             text="JobScraper Pro",
                             font=("Helvetica", 24, "bold"),
                             fg="white",
                             bg="#4a90e2")
        title_label.pack()

        # Main content
        main_frame = tk.Frame(self.root, bg="#f0f2f5")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Search section
        search_frame = tk.Frame(main_frame, bg="white", bd=2, relief="flat")
        search_frame.pack(pady=10, padx=10, fill="x")
        
        self.url_entry = ttk.Entry(search_frame, 
                                 width=50,
                                 font=('Helvetica', 12))
        self.url_entry.insert(0, "https://example.com/jobs")
        self.url_entry.pack(side="left", padx=10, pady=10)

        self.scrape_button = ttk.Button(search_frame,
                                      text="Start Scraping",
                                      style="Custom.TButton",
                                      command=self.start_scraping_thread)
        self.scrape_button.pack(side="left", padx=10)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, 
                                      length=400, 
                                      mode='indeterminate')
        self.progress.pack(pady=10)

        # Results area
        self.results_text = tk.Text(main_frame, 
                                  height=20, 
                                  width=80,
                                  font=('Helvetica', 11),
                                  bd=0,
                                  bg="white",
                                  relief="flat")
        self.results_text.pack(pady=10, padx=10, fill="both", expand=True)

        # Animation canvas
        self.canvas = tk.Canvas(main_frame, 
                              width=100, 
                              height=100, 
                              bg="#f0f2f5", 
                              highlightthickness=0)
        self.canvas.pack(pady=10)
        self.animate_circle()

    def animate_circle(self):
        self.canvas.delete("all")
        if self.is_scraping:
            for i in range(4):
                self.canvas.create_oval(20 + i*20, 40, 40 + i*20, 60,
                                      fill="#4a90e2" if i % 2 == 0 else "#357abd",
                                      outline="")
        self.root.after(200, self.animate_circle)

    def start_scraping_thread(self):
        if not self.is_scraping:
            thread = threading.Thread(target=self.scrape_jobs)
            thread.start()

    def scrape_jobs(self):
        self.is_scraping = True
        self.progress.start(10)
        self.scrape_button.configure(text="Scraping...")
        self.results_text.delete(1.0, tk.END)
        
        url = self.url_entry.get()
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Example scraping logic (modify based on target website structure)
            jobs = soup.find_all('div', class_='job-listing')  # Adjust class name
            if not jobs:
                jobs = soup.find_all('li', class_='job')  # Alternative structure
                
            for job in jobs[:10]:  # Limit to 10 jobs for demo
                title = job.find('h2') or job.find('h3')
                company = job.find('span', class_='company')
                location = job.find('span', class_='location')
                
                job_info = f"Title: {title.text if title else 'N/A'}\n"
                job_info += f"Company: {company.text if company else 'N/A'}\n"
                job_info += f"Location: {location.text if location else 'N/A'}\n"
                job_info += "-" * 50 + "\n"
                
                self.results_text.insert(tk.END, job_info)
                self.results_text.update()
                time.sleep(0.1)  # Smooth scrolling effect
                
            if not jobs:
                self.results_text.insert(tk.END, "No job listings found or invalid URL.\n")
                
        except Exception as e:
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
            
        self.progress.stop()
        self.is_scraping = False
        self.scrape_button.configure(text="Start Scraping")

if __name__ == "__main__":
    root = tk.Tk()
    app = JobScraperApp(root)
    root.mainloop()
