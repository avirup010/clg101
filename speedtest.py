import tkinter as tk
from tkinter import ttk, messagebox
import requests
import time
import threading

class SpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internet Speed Test")
        self.root.geometry("500x300")
        self.root.configure(bg="#1e1e2e")  # Dark theme background

        # Style for modern look
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.configure("TLabel", font=("Helvetica", 14), background="#1e1e2e", foreground="#ffffff")
        style.configure("TProgressbar", thickness=5)

        # Main frame for centering content
        self.main_frame = tk.Frame(root, bg="#1e1e2e")
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Result label (fixed string literal)
        self.result_label = ttk.Label(self.main_frame, text="Click 'Start Test' to begin", style="TLabel")
        self.result_label.pack(pady=20)

        # Progress bar (hidden initially)
        self.progress = ttk.Progressbar(self.main_frame, mode="indeterminate", length=300)
        self.progress.pack(pady=10)
        self.progress.pack_forget()  # Hide until test starts

        # Start test button with rounded appearance
        self.start_button = ttk.Button(
            self.main_frame, text="Start Test", style="TButton", command=self.start_test_thread
        )
        self.start_button.pack(pady=20)

        # Button hover effect
        self.start_button.bind("<Enter>", lambda e: self.start_button.configure(style="Hover.TButton"))
        self.start_button.bind("<Leave>", lambda e: self.start_button.configure(style="TButton"))
        style.configure("Hover.TButton", background="#3b82f6", foreground="#ffffff")
        style.map("TButton", background=[("active", "#3b82f6")])

        self.testing = False

    def start_test_thread(self):
        if not self.testing:
            self.testing = True
            self.start_button.configure(state="disabled")
            self.progress.pack()  # Show progress bar
            self.progress.start(10)  # Start indeterminate animation
            threading.Thread(target=self.run_speed_test, daemon=True).start()

    def run_speed_test(self):
        self.result_label.config(text="Testing... Please wait")
        self.root.update()

        # Test file URLs (primary and fallbacks)
        test_urls = [
            ("http://speedtest.tele2.net/100MB.zip", 100, "Tele2"),
            ("http://ipv4.download.thinkbroadband.com/100MB.zip", 100, "ThinkBroadband"),
            ("http://proof.ovh.net/files/100Mb.dat", 100, "OVH"),
            ("https://cloudflare-quic.com/speedtest/100MB.bin", 100, "Cloudflare")
        ]

        speed_mbps = 0.0
        error_messages = []
        max_retries = 2

        for url, file_size_mb, server_name in test_urls:
            for attempt in range(max_retries):
                try:
                    start_time = time.time()
                    response = requests.get(url, stream=True, timeout=10)
                    response.raise_for_status()

                    total_downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        total_downloaded += len(chunk)

                    end_time = time.time()
                    duration = end_time - start_time

                    if duration > 0:
                        speed_mbps = (file_size_mb * 8) / duration  # Convert MB to Mb
                        self.root.after(0, self.update_ui, speed_mbps, None)
                        return  # Success, exit function
                    else:
                        error_messages.append(f"{server_name}: Download duration too short")
                        break
                except requests.RequestException as e:
                    error_messages.append(f"{server_name} (Attempt {attempt + 1}): {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retry
                    continue  # Try next attempt or server

        self.root.after(0, self.update_ui, 0.0, error_messages)

    def update_ui(self, speed_mbps, error_messages):
        self.progress.stop()
        self.progress.pack_forget()  # Hide progress bar
        self.start_button.configure(state="normal")
        self.testing = False

        if speed_mbps > 0:
            self.result_label.config(text=f"Download Speed: {speed_mbps:.2f} Mbps")
        else:
            self.result_label.config(text="Test failed. Could not connect to servers.")
            error_detail = "Errors:\n" + "\n".join(error_messages) if error_messages else "Unknown error."
            messagebox.showerror("Error", error_detail)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTestApp(root)
    root.mainloop()