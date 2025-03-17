import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import csv
import re
import os
import json
from string import Template
import threading

class EmailSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personalized Email Sender")
        self.root.geometry("900x700")
        self.root.configure(bg="#f5f5f5")
        
        # Set theme
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure styles
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TButton", background="#4CAF50", foreground="black", font=("Segoe UI", 10))
        style.configure("TLabel", background="#f5f5f5", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#f5f5f5", font=("Segoe UI", 16, "bold"))
        style.configure("Subheader.TLabel", background="#f5f5f5", font=("Segoe UI", 12, "bold"))

        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.setup_tab = ttk.Frame(self.notebook)
        self.template_tab = ttk.Frame(self.notebook)
        self.recipients_tab = ttk.Frame(self.notebook)
        self.send_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.setup_tab, text="SMTP Setup")
        self.notebook.add(self.template_tab, text="Email Template")
        self.notebook.add(self.recipients_tab, text="Recipients")
        self.notebook.add(self.send_tab, text="Send Emails")
        
        # Initialize variables
        self.smtp_server = tk.StringVar(value="smtp.gmail.com")
        self.smtp_port = tk.IntVar(value=587)
        self.email = tk.StringVar()
        self.password = tk.StringVar()
        self.subject = tk.StringVar()
        self.recipient_file_path = tk.StringVar()
        self.attachments = []
        
        # Create UI for each tab
        self.setup_smtp_tab()
        self.setup_template_tab()
        self.setup_recipients_tab()
        self.setup_send_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load settings if they exist
        self.load_settings()

    def setup_smtp_tab(self):
        # Header
        header = ttk.Label(self.setup_tab, text="SMTP Server Configuration", style="Header.TLabel")
        header.pack(pady=(0, 20))
        
        # Frame for form
        form_frame = ttk.Frame(self.setup_tab)
        form_frame.pack(fill=tk.BOTH, padx=30, pady=10)
        
        # SMTP Server
        ttk.Label(form_frame, text="SMTP Server:").grid(row=0, column=0, sticky=tk.W, pady=10)
        ttk.Entry(form_frame, textvariable=self.smtp_server, width=40).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # SMTP Port
        ttk.Label(form_frame, text="SMTP Port:").grid(row=1, column=0, sticky=tk.W, pady=10)
        ttk.Entry(form_frame, textvariable=self.smtp_port, width=10).grid(row=1, column=1, sticky=tk.W, padx=10)
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=10)
        ttk.Entry(form_frame, textvariable=self.email, width=40).grid(row=2, column=1, sticky=tk.W, padx=10)
        
        # Password
        ttk.Label(form_frame, text="Password or App Password:").grid(row=3, column=0, sticky=tk.W, pady=10)
        ttk.Entry(form_frame, textvariable=self.password, show="*", width=40).grid(row=3, column=1, sticky=tk.W, padx=10)
        
        # Info text
        info_text = """Note: For Gmail, you'll need to use an App Password instead of your regular password. 
Go to your Google Account → Security → 2-Step Verification → App Passwords to create one."""
        
        info_label = ttk.Label(form_frame, text=info_text, wraplength=400)
        info_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=20)
        
        # Test connection button
        test_btn = ttk.Button(form_frame, text="Test Connection", command=self.test_connection)
        test_btn.grid(row=5, column=0, sticky=tk.W, pady=10)
        
        # Save settings button
        save_btn = ttk.Button(form_frame, text="Save Settings", command=self.save_settings)
        save_btn.grid(row=5, column=1, sticky=tk.W, padx=10, pady=10)

    def setup_template_tab(self):
        # Header
        header = ttk.Label(self.template_tab, text="Email Template", style="Header.TLabel")
        header.pack(pady=(0, 20))
        
        # Subject frame
        subject_frame = ttk.Frame(self.template_tab)
        subject_frame.pack(fill=tk.X, padx=30, pady=10)
        
        ttk.Label(subject_frame, text="Subject:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(subject_frame, textvariable=self.subject, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Body frame
        body_frame = ttk.Frame(self.template_tab)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        ttk.Label(body_frame, text="Email Body:").pack(anchor=tk.W, pady=(0, 5))
        
        # Template variables info
        template_info = ttk.Label(body_frame, text="Use ${variable_name} for personalization variables (e.g., ${name}, ${company})", 
                                  foreground="#555555")
        template_info.pack(anchor=tk.W, pady=(0, 10))
        
        # Text editor
        self.body_text = scrolledtext.ScrolledText(body_frame, wrap=tk.WORD, height=15, width=80)
        self.body_text.pack(fill=tk.BOTH, expand=True)
        
        # Default text
        default_text = """Dear ${name},

I hope this email finds you well. I wanted to reach out regarding ${topic}.

Best regards,
Your Name"""
        self.body_text.insert(tk.END, default_text)
        
        # Attachments frame
        attachment_frame = ttk.Frame(self.template_tab)
        attachment_frame.pack(fill=tk.X, padx=30, pady=10)
        
        ttk.Label(attachment_frame, text="Attachments:").pack(anchor=tk.W, pady=(10, 5))
        
        # Attachment buttons
        btn_frame = ttk.Frame(attachment_frame)
        btn_frame.pack(fill=tk.X)
        
        add_btn = ttk.Button(btn_frame, text="Add Attachment", command=self.add_attachment)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(btn_frame, text="Clear Attachments", command=self.clear_attachments)
        clear_btn.pack(side=tk.LEFT)
        
        # Attachment list
        self.attachment_listbox = tk.Listbox(attachment_frame, height=4, width=80)
        self.attachment_listbox.pack(fill=tk.X, pady=10)

    def setup_recipients_tab(self):
        # Header
        header = ttk.Label(self.recipients_tab, text="Recipients List", style="Header.TLabel")
        header.pack(pady=(0, 20))
        
        # Import frame
        import_frame = ttk.Frame(self.recipients_tab)
        import_frame.pack(fill=tk.X, padx=30, pady=10)
        
        ttk.Label(import_frame, text="CSV File:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(import_frame, textvariable=self.recipient_file_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(import_frame, text="Browse", command=self.browse_csv).pack(side=tk.LEFT)
        
        # Info text
        info_text = """The CSV file should have headers. Column names will be used as template variables.
For example, if you have columns 'name', 'email', 'company', you can use ${name}, ${email}, and ${company} in your template."""
        
        info_label = ttk.Label(self.recipients_tab, text=info_text, wraplength=700)
        info_label.pack(anchor=tk.W, padx=30, pady=10)
        
        # Preview frame
        preview_frame = ttk.Frame(self.recipients_tab)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        ttk.Label(preview_frame, text="Preview:", style="Subheader.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        # Preview in a treeview
        self.preview_tree = ttk.Treeview(preview_frame)
        self.preview_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(self.preview_tree, orient="vertical", command=self.preview_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
        
        # Load button
        load_btn = ttk.Button(self.recipients_tab, text="Load Recipients", command=self.load_recipients)
        load_btn.pack(pady=10)

    def setup_send_tab(self):
        # Header
        header = ttk.Label(self.send_tab, text="Send Emails", style="Header.TLabel")
        header.pack(pady=(0, 20))
        
        # Preview frame
        preview_frame = ttk.Frame(self.send_tab)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        ttk.Label(preview_frame, text="Preview of first email:", style="Subheader.TLabel").pack(anchor=tk.W, pady=(0, 5))

        self.preview_subject = ttk.Label(preview_frame, text="Subject: ")
        self.preview_subject.pack(anchor=tk.W, pady=(10, 5))
        
        # Preview text
        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, height=10, width=80)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.config(state=tk.DISABLED)
        
        # Options frame
        options_frame = ttk.Frame(self.send_tab)
        options_frame.pack(fill=tk.X, padx=30, pady=10)
        
        # Send options
        ttk.Label(options_frame, text="Send Options:", style="Subheader.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        # Delay between emails
        delay_frame = ttk.Frame(options_frame)
        delay_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(delay_frame, text="Delay between emails (seconds):").pack(side=tk.LEFT, padx=(0, 10))
        self.delay_var = tk.IntVar(value=5)
        ttk.Spinbox(delay_frame, from_=1, to=60, textvariable=self.delay_var, width=5).pack(side=tk.LEFT)
        
        # Send button
        btn_frame = ttk.Frame(self.send_tab)
        btn_frame.pack(fill=tk.X, padx=30, pady=20)
        
        self.send_btn = ttk.Button(btn_frame, text="Send Emails", command=self.send_emails)
        self.send_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.preview_btn = ttk.Button(btn_frame, text="Generate Preview", command=self.generate_preview)
        self.preview_btn.pack(side=tk.LEFT)
        
        # Progress bar
        ttk.Label(self.send_tab, text="Progress:").pack(anchor=tk.W, padx=30, pady=(10, 5))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.send_tab, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=30, pady=(0, 10))
        
        # Status label
        self.send_status_var = tk.StringVar(value="Ready to send")
        self.send_status_label = ttk.Label(self.send_tab, textvariable=self.send_status_var)
        self.send_status_label.pack(anchor=tk.W, padx=30)

    def browse_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.recipient_file_path.set(file_path)

    def add_attachment(self):
        file_paths = filedialog.askopenfilenames()
        for file_path in file_paths:
            if file_path and file_path not in self.attachments:
                self.attachments.append(file_path)
                self.attachment_listbox.insert(tk.END, os.path.basename(file_path))

    def clear_attachments(self):
        self.attachments = []
        self.attachment_listbox.delete(0, tk.END)

    def test_connection(self):
        try:
            server = smtplib.SMTP(self.smtp_server.get(), self.smtp_port.get())
            server.ehlo()
            server.starttls()
            server.login(self.email.get(), self.password.get())
            server.quit()
            messagebox.showinfo("Success", "Connection successful!")
            self.status_var.set("SMTP connection tested successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
            self.status_var.set("SMTP connection test failed")

    def save_settings(self):
        settings = {
            "smtp_server": self.smtp_server.get(),
            "smtp_port": self.smtp_port.get(),
            "email": self.email.get()
            # Not saving password for security reasons
        }
        
        try:
            with open("email_settings.json", "w") as f:
                json.dump(settings, f)
            self.status_var.set("Settings saved successfully")
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            self.status_var.set("Failed to save settings")

    def load_settings(self):
        try:
            if os.path.exists("email_settings.json"):
                with open("email_settings.json", "r") as f:
                    settings = json.load(f)
                
                self.smtp_server.set(settings.get("smtp_server", "smtp.gmail.com"))
                self.smtp_port.set(settings.get("smtp_port", 587))
                self.email.set(settings.get("email", ""))
                self.status_var.set("Settings loaded successfully")
        except Exception as e:
            self.status_var.set(f"Failed to load settings: {str(e)}")

    def load_recipients(self):
        file_path = self.recipient_file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid CSV file")
            return
            
        try:
            # Clear existing treeview
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
                
            # Read CSV file
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)
                
                # Configure treeview columns
                self.preview_tree['columns'] = headers
                self.preview_tree['show'] = 'headings'
                
                for header in headers:
                    self.preview_tree.heading(header, text=header)
                    self.preview_tree.column(header, width=100)
                
                # Add rows
                for i, row in enumerate(reader):
                    if i >= 100:  # Limit to first 100 rows for preview
                        break
                    self.preview_tree.insert('', tk.END, values=row)
                
            self.status_var.set(f"Loaded recipients from {os.path.basename(file_path)}")
            messagebox.showinfo("Success", "Recipients loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load recipients: {str(e)}")
            self.status_var.set("Failed to load recipients")

    def generate_preview(self):
        file_path = self.recipient_file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please load recipients first")
            return
            
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                try:
                    first_recipient = next(reader)
                except StopIteration:
                    messagebox.showerror("Error", "CSV file is empty or has no data rows")
                    return

                # Get template content
                subject_template = Template(self.subject.get())
                body_template = Template(self.body_text.get('1.0', tk.END))
                
                # Fill in template for preview
                try:
                    subject = subject_template.substitute(first_recipient)
                    body = body_template.substitute(first_recipient)
                    
                    # Update preview
                    self.preview_subject.config(text=f"Subject: {subject}")
                    
                    self.preview_text.config(state=tk.NORMAL)
                    self.preview_text.delete('1.0', tk.END)
                    self.preview_text.insert('1.0', body)
                    self.preview_text.config(state=tk.DISABLED)
                    
                    self.send_status_var.set("Preview generated")
                    
                except KeyError as e:
                    messagebox.showerror("Template Error", f"Variable {e} not found in CSV headers")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate preview: {str(e)}")

    def send_emails(self):
        # Validate inputs
        if not self.smtp_server.get() or not self.smtp_port.get() or not self.email.get() or not self.password.get():
            messagebox.showerror("Error", "Please complete SMTP setup first")
            return
            
        if not self.subject.get() or not self.body_text.get('1.0', tk.END).strip():
            messagebox.showerror("Error", "Please complete email template first")
            return
            
        file_path = self.recipient_file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please load recipients first")
            return
            
        # Ask for confirmation
        total_recipients = sum(1 for _ in open(file_path)) - 1  # Subtract header row
        if not messagebox.askyesno("Confirm", f"Send personalized emails to {total_recipients} recipients?"):
            return
            
        # Disable send button and update status
        self.send_btn.config(state=tk.DISABLED)
        self.send_status_var.set("Preparing to send emails...")
        
        # Start sending in a separate thread
        send_thread = threading.Thread(target=self._send_emails_thread, args=(total_recipients,))
        send_thread.daemon = True
        send_thread.start()

    def _send_emails_thread(self, total_recipients):
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server.get(), self.smtp_port.get())
            server.ehlo()
            server.starttls()
            server.login(self.email.get(), self.password.get())
            
            # Get templates
            subject_template = Template(self.subject.get())
            body_template = Template(self.body_text.get('1.0', tk.END))
            
            # Process recipients
            with open(self.recipient_file_path.get(), 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for i, recipient in enumerate(reader):
                    try:
                        # Update progress
                        progress = (i / total_recipients) * 100
                        self.progress_var.set(progress)
                        self.send_status_var.set(f"Sending email {i+1}/{total_recipients}...")
                        
                        # Create personalized email
                        email_subject = subject_template.substitute(recipient)
                        email_body = body_template.substitute(recipient)
                        
                        # Create message
                        msg = MIMEMultipart()
                        msg['From'] = self.email.get()
                        msg['To'] = recipient.get('email', '')
                        msg['Subject'] = email_subject
                        
                        # Attach body
                        msg.attach(MIMEText(email_body, 'plain'))
                        
                        # Add attachments
                        for attachment in self.attachments:
                            with open(attachment, 'rb') as f:
                                attach = MIMEApplication(f.read())
                                attach.add_header('Content-Disposition', 'attachment', 
                                                 filename=os.path.basename(attachment))
                                msg.attach(attach)
                        
                        # Send email
                        server.send_message(msg)
                        
                        # Delay between emails
                        time.sleep(self.delay_var.get())
                        
                    except KeyError as e:
                        self.root.after(0, lambda: messagebox.showerror("Template Error", 
                                                                      f"Variable {e} not found for recipient {i+1}"))
                        break
                    except Exception as e:
                        self.root.after(0, lambda: messagebox.showerror("Send Error", 
                                                                      f"Failed to send email to recipient {i+1}: {str(e)}"))
                        continue
            
            # Close connection
            server.quit()
            
            # Update UI
            self.progress_var.set(100)
            self.send_status_var.set(f"Complete! Sent {total_recipients} emails.")
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Successfully sent {total_recipients} emails!"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to send emails: {str(e)}"))
            self.send_status_var.set("Failed to send emails")
            
        finally:
            # Re-enable send button
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))

def main():
    # Import necessary modules inside function to avoid circular imports
    import time
    
    root = tk.Tk()
    app = EmailSenderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()