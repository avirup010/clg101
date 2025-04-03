"""
Indian Government Form Filler Application

A user-friendly desktop application that simplifies the process of filling Indian government forms.
This application provides a familiar interface inspired by the Passport Seva portal with features including:
- Multiple form types (Passport, Aadhar, PAN, Voter ID, Driving License)
- Step-by-step guided form completion
- Document upload functionality
- Application tracking
- Save and resume capability
- Help and support section

The application aims to make government paperwork less intimidating by providing
clear instructions, validation, and a consistent interface across different form types.

Created: April 2025
"""


import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json
import os
from datetime import datetime

class IndianFormFillerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Indian Government Form Filler")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # Set app icon and styling
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", background="#FF9933", foreground="black", font=("Arial", 10, "bold"))
        self.style.map("TButton", background=[("active", "#FF8000")])
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("Header.TLabel", background="#FF9933", foreground="white", font=("Arial", 12, "bold"))
        self.style.configure("Title.TLabel", background="#f0f0f0", foreground="#138808", font=("Arial", 16, "bold"))
        
        # Header
        self.header_frame = ttk.Frame(self.root)
        self.header_frame.pack(fill=tk.X)
        
        # Logo and title
        self.logo_frame = ttk.Frame(self.header_frame)
        self.logo_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Load a placeholder for the emblem
        self.emblem_img = tk.PhotoImage(width=50, height=50)
        self.emblem_label = ttk.Label(self.logo_frame, image=self.emblem_img)
        self.emblem_label.pack(side=tk.LEFT)
        
        self.title_frame = ttk.Frame(self.header_frame)
        self.title_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.title_label = ttk.Label(self.title_frame, text="Indian Government Form Filler", style="Title.TLabel")
        self.title_label.pack(anchor=tk.W)
        
        self.subtitle_label = ttk.Label(self.title_frame, text="Simplifying form filling process for Indian citizens")
        self.subtitle_label.pack(anchor=tk.W)
        
        # User info
        self.user_frame = ttk.Frame(self.header_frame)
        self.user_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        self.user_label = ttk.Label(self.user_frame, text="Welcome, User")
        self.user_label.pack(anchor=tk.E)
        
        self.logout_btn = ttk.Button(self.user_frame, text="Logout", command=self.logout)
        self.logout_btn.pack(anchor=tk.E, pady=5)
        
        # Navigation bar
        self.nav_frame = ttk.Frame(self.root, style="TFrame")
        self.nav_frame.pack(fill=tk.X)
        
        self.nav_buttons = [
            ("Home", self.show_home),
            ("Form Selection", self.show_form_selection),
            ("My Applications", self.show_my_applications),
            ("Track Status", self.show_track_status),
            ("Help", self.show_help)
        ]
        
        for text, command in self.nav_buttons:
            btn = ttk.Button(self.nav_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Main content frame
        self.content_frame = ttk.Frame(self.root, style="TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Status bar
        self.status_frame = ttk.Frame(self.root, style="TFrame")
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Initialize forms database
        self.forms = {
            "passport": {
                "name": "Passport Application",
                "sections": ["Personal Details", "Family Details", "Address Details", "References", "Documents Upload"]
            },
            "aadhar": {
                "name": "Aadhar Card Update",
                "sections": ["Personal Details", "Address Details", "Biometric Details", "Documents Upload"]
            },
            "pan": {
                "name": "PAN Card Application",
                "sections": ["Personal Details", "Contact Details", "Identity Proof", "Documents Upload"]
            },
            "voter": {
                "name": "Voter ID Application",
                "sections": ["Personal Details", "Residential Details", "Family Details", "Documents Upload"]
            },
            "driving": {
                "name": "Driving License Application",
                "sections": ["Personal Details", "License Type", "Address Details", "Documents Upload"]
            }
        }
        
        # User data storage
        self.user_data = {}
        self.current_form = None
        self.current_section = None
        
        # Show the home screen by default
        self.show_home()
    
    def show_home(self):
        self.clear_content()
        
        welcome_label = ttk.Label(self.content_frame, text="Welcome to Indian Government Form Filler", style="Title.TLabel")
        welcome_label.pack(pady=20)
        
        info_label = ttk.Label(self.content_frame, text="This application helps you fill various Indian government forms with ease.")
        info_label.pack(pady=10)
        
        start_button = ttk.Button(self.content_frame, text="Start New Application", command=self.show_form_selection)
        start_button.pack(pady=20)
        
        # News and updates section
        news_frame = ttk.LabelFrame(self.content_frame, text="News and Updates")
        news_frame.pack(fill=tk.X, pady=20, padx=50)
        
        news_items = [
            "New Passport Rules 2025: Documentation requirements simplified",
            "Aadhar Update: Now link your mobile number online",
            "PAN-Aadhar Linking: Last date extended to June 30, 2025",
            "Digital Voter ID available for download from Election Commission website"
        ]
        
        for news in news_items:
            news_label = ttk.Label(news_frame, text="• " + news)
            news_label.pack(anchor=tk.W, pady=5, padx=10)
    
    def show_form_selection(self):
        self.clear_content()
        
        selection_label = ttk.Label(self.content_frame, text="Select a Form to Fill", style="Title.TLabel")
        selection_label.pack(pady=20)
        
        forms_frame = ttk.Frame(self.content_frame)
        forms_frame.pack(pady=20)
        
        for form_id, form_data in self.forms.items():
            form_button = ttk.Button(
                forms_frame, 
                text=form_data["name"], 
                command=lambda fid=form_id: self.select_form(fid)
            )
            form_button.pack(fill=tk.X, pady=5, padx=100)
    
    def select_form(self, form_id):
        self.current_form = form_id
        self.current_section = 0
        
        # Initialize user data for this form if it doesn't exist
        if form_id not in self.user_data:
            self.user_data[form_id] = {section: {} for section in self.forms[form_id]["sections"]}
        
        self.show_form_instruction()
    
    def show_form_instruction(self):
        self.clear_content()
        
        form_name = self.forms[self.current_form]["name"]
        
        instruction_label = ttk.Label(self.content_frame, text=f"{form_name} - Instructions", style="Title.TLabel")
        instruction_label.pack(pady=20)
        
        instructions_frame = ttk.LabelFrame(self.content_frame, text="Please Read Carefully")
        instructions_frame.pack(fill=tk.X, padx=50, pady=20)
        
        instructions = [
            "Ensure all information provided is accurate and matches your documents.",
            "Keep all required documents ready in digital format (PDF/JPG) before proceeding.",
            "All fields marked with * are mandatory.",
            "The application process has multiple sections. You can save and resume later.",
            "After submission, you will receive an application reference number for tracking."
        ]
        
        for instruction in instructions:
            inst_label = ttk.Label(instructions_frame, text="• " + instruction, wraplength=700)
            inst_label.pack(anchor=tk.W, pady=5, padx=10)
        
        docs_required_frame = ttk.LabelFrame(self.content_frame, text="Documents Required")
        docs_required_frame.pack(fill=tk.X, padx=50, pady=20)
        
        form_docs = {
            "passport": ["Address Proof", "Identity Proof", "Birth Certificate", "Passport Size Photo"],
            "aadhar": ["Address Proof", "Identity Proof", "Recent Photograph"],
            "pan": ["Identity Proof", "Address Proof", "Photograph", "Signature Scan"],
            "voter": ["Address Proof", "Age Proof", "Passport Size Photos"],
            "driving": ["Address Proof", "Identity Proof", "Medical Certificate", "Passport Size Photos"]
        }
        
        for doc in form_docs.get(self.current_form, []):
            doc_label = ttk.Label(docs_required_frame, text="• " + doc)
            doc_label.pack(anchor=tk.W, pady=5, padx=10)
        
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=30)
        
        back_btn = ttk.Button(button_frame, text="Back", command=self.show_form_selection)
        back_btn.pack(side=tk.LEFT, padx=10)
        
        proceed_btn = ttk.Button(button_frame, text="Proceed to Form", command=self.show_form_section)
        proceed_btn.pack(side=tk.LEFT, padx=10)
    
    def show_form_section(self):
        self.clear_content()
        
        form_name = self.forms[self.current_form]["name"]
        sections = self.forms[self.current_form]["sections"]
        current_section_name = sections[self.current_section]
        
        # Header
        section_label = ttk.Label(
            self.content_frame, 
            text=f"{form_name} - {current_section_name}",
            style="Title.TLabel"
        )
        section_label.pack(pady=20)
        
        # Progress indicator
        progress_frame = ttk.Frame(self.content_frame)
        progress_frame.pack(fill=tk.X, padx=50, pady=10)
        
        for i, section in enumerate(sections):
            style = "TButton"
            if i < self.current_section:
                btn_text = f"✓ {section}"
            elif i == self.current_section:
                btn_text = f"➤ {section}"
                style = "TButton"
            else:
                btn_text = section
            
            section_btn = ttk.Button(
                progress_frame,
                text=btn_text,
                command=lambda idx=i: self.navigate_to_section(idx)
            )
            section_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Form fields - different for each section
        form_frame = ttk.LabelFrame(self.content_frame, text=f"Fill {current_section_name}")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        self.form_fields = {}
        
        if current_section_name == "Personal Details":
            fields = [
                ("Full Name (as in documents)*", "name"),
                ("Date of Birth (DD/MM/YYYY)*", "dob"),
                ("Gender*", "gender", ["Male", "Female", "Other"]),
                ("Marital Status", "marital", ["Single", "Married", "Divorced", "Widowed"]),
                ("Place of Birth*", "birth_place"),
                ("Mobile Number*", "mobile"),
                ("Email Address*", "email")
            ]
        elif current_section_name == "Family Details":
            fields = [
                ("Father's Name*", "father_name"),
                ("Father's Nationality*", "father_nationality"),
                ("Mother's Name*", "mother_name"),
                ("Mother's Nationality*", "mother_nationality"),
                ("Spouse Name (if applicable)", "spouse_name")
            ]
        elif current_section_name == "Address Details":
            fields = [
                ("House No./Apartment*", "house_no"),
                ("Street/Locality*", "street"),
                ("Village/Town/City*", "city"),
                ("District*", "district"),
                ("State*", "state"),
                ("Pin Code*", "pincode"),
                ("Duration at current address (Years)*", "address_duration")
            ]
        elif current_section_name == "References":
            fields = [
                ("Reference 1 Name*", "ref1_name"),
                ("Reference 1 Address*", "ref1_address"),
                ("Reference 1 Phone*", "ref1_phone"),
                ("Reference 2 Name*", "ref2_name"),
                ("Reference 2 Address*", "ref2_address"),
                ("Reference 2 Phone*", "ref2_phone")
            ]
        elif current_section_name == "Documents Upload":
            fields = [
                ("Identity Proof*", "id_proof", "file"),
                ("Address Proof*", "address_proof", "file"),
                ("Photograph*", "photo", "file"),
                ("Signature*", "signature", "file")
            ]
        elif current_section_name == "License Type":
            fields = [
                ("License Type*", "license_type", ["Learner's License", "Permanent License", "International Driving Permit"]),
                ("Vehicle Class*", "vehicle_class", ["Two Wheeler", "Light Motor Vehicle", "Heavy Motor Vehicle", "Commercial"])
            ]
        elif current_section_name == "Biometric Details":
            fields = [
                ("Biometric Status", "biometric_status", ["Captured", "Exempted", "Not Captured"]),
                ("Biometric Exemption Reason (if applicable)", "biometric_exemption")
            ]
        elif current_section_name == "Contact Details":
            fields = [
                ("Phone Number*", "phone"),
                ("Alternative Phone", "alt_phone"),
                ("Email Address*", "email"),
                ("Preferred Communication Mode*", "comm_mode", ["SMS", "Email", "Both"])
            ]
        elif current_section_name == "Identity Proof":
            fields = [
                ("Identity Document Type*", "id_type", ["Aadhaar Card", "Voter ID", "Passport", "Driving License"]),
                ("Document Number*", "id_number"),
                ("Issuing Authority*", "id_authority"),
                ("Date of Issue (DD/MM/YYYY)*", "id_issue_date")
            ]
        elif current_section_name == "Residential Details":
            fields = [
                ("Residing since (MM/YYYY)*", "residing_since"),
                ("Type of Residence*", "residence_type", ["Owned", "Rented", "Family Owned", "Employer Provided"]),
                ("Assembly Constituency*", "constituency")
            ]
        else:
            fields = []
        
        # Create form fields
        for i, field_info in enumerate(fields):
            field_frame = ttk.Frame(form_frame)
            field_frame.pack(fill=tk.X, pady=5, padx=10)
            
            if len(field_info) == 2:  # Text field
                label, key = field_info
                ttk.Label(field_frame, text=label).pack(side=tk.LEFT, padx=5)
                
                entry = ttk.Entry(field_frame, width=40)
                entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                
                # Pre-fill if data exists
                if key in self.user_data[self.current_form][current_section_name]:
                    entry.insert(0, self.user_data[self.current_form][current_section_name][key])
                
                self.form_fields[key] = entry
                
            elif len(field_info) == 3 and field_info[2] != "file":  # Dropdown
                label, key, options = field_info
                ttk.Label(field_frame, text=label).pack(side=tk.LEFT, padx=5)
                
                var = tk.StringVar()
                dropdown = ttk.Combobox(field_frame, textvariable=var, values=options, state="readonly", width=38)
                dropdown.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                
                # Pre-fill if data exists
                if key in self.user_data[self.current_form][current_section_name]:
                    var.set(self.user_data[self.current_form][current_section_name][key])
                
                self.form_fields[key] = var
                
            elif len(field_info) == 3 and field_info[2] == "file":  # File upload
                label, key, _ = field_info
                ttk.Label(field_frame, text=label).pack(side=tk.LEFT, padx=5)
                
                var = tk.StringVar()
                entry = ttk.Entry(field_frame, textvariable=var, width=30)
                entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                
                # Pre-fill if data exists
                if key in self.user_data[self.current_form][current_section_name]:
                    var.set(self.user_data[self.current_form][current_section_name][key])
                
                upload_btn = ttk.Button(
                    field_frame, 
                    text="Browse", 
                    command=lambda v=var: self.browse_file(v)
                )
                upload_btn.pack(side=tk.LEFT, padx=5)
                
                self.form_fields[key] = var
        
        # Buttons
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=20)
        
        back_btn = ttk.Button(button_frame, text="Back", command=self.back_action)
        back_btn.pack(side=tk.LEFT, padx=10)
        
        save_btn = ttk.Button(button_frame, text="Save", command=self.save_form_data)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        if self.current_section < len(sections) - 1:
            next_text = "Next"
            next_command = self.next_section
        else:
            next_text = "Submit Application"
            next_command = self.submit_application
        
        next_btn = ttk.Button(button_frame, text=next_text, command=next_command)
        next_btn.pack(side=tk.LEFT, padx=10)
    
    def browse_file(self, var):
        filename = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png"), ("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if filename:
            var.set(filename)
    
    def save_form_data(self):
        current_section_name = self.forms[self.current_form]["sections"][self.current_section]
        
        # Save form data
        for key, field in self.form_fields.items():
            if hasattr(field, 'get'):
                value = field.get()
            else:
                value = field
            
            self.user_data[self.current_form][current_section_name][key] = value
        
        messagebox.showinfo("Save Success", "Your data has been saved successfully.")
        self.status_label.config(text=f"Form data saved at {datetime.now().strftime('%H:%M:%S')}")
    
    def next_section(self):
        self.save_form_data()
        
        if self.current_section < len(self.forms[self.current_form]["sections"]) - 1:
            self.current_section += 1
            self.show_form_section()
    
    def back_action(self):
        if self.current_section > 0:
            self.current_section -= 1
            self.show_form_section()
        else:
            self.show_form_instruction()
    
    def navigate_to_section(self, section_index):
        # Only allow navigating to completed sections or the current one
        if section_index <= self.current_section:
            self.current_section = section_index
            self.show_form_section()
    
    def submit_application(self):
        self.save_form_data()
        
        # Generate application ID
        import random
        application_id = f"APP{random.randint(100000, 999999)}"
        
        # In a real application, here you would send data to a server
        
        self.clear_content()
        
        success_label = ttk.Label(
            self.content_frame, 
            text="Application Submitted Successfully!",
            style="Title.TLabel"
        )
        success_label.pack(pady=20)
        
        app_id_label = ttk.Label(
            self.content_frame,
            text=f"Your Application Reference Number: {application_id}",
            font=("Arial", 12, "bold")
        )
        app_id_label.pack(pady=20)
        
        info_text = """
        Your application has been submitted successfully. Please note down 
        your application reference number for future correspondence.
        
        You will receive updates on your registered mobile number and email address.
        
        Please check your email for a confirmation and next steps.
        """
        
        info_label = ttk.Label(self.content_frame, text=info_text, wraplength=600)
        info_label.pack(pady=20)
        
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=30)
        
        home_btn = ttk.Button(button_frame, text="Back to Home", command=self.show_home)
        home_btn.pack(side=tk.LEFT, padx=10)
        
        print_btn = ttk.Button(button_frame, text="Print Acknowledgement", command=self.print_acknowledgement)
        print_btn.pack(side=tk.LEFT, padx=10)
    
    def show_my_applications(self):
        self.clear_content()
        
        title_label = ttk.Label(self.content_frame, text="My Applications", style="Title.TLabel")
        title_label.pack(pady=20)
        
        if not any(self.user_data):
            empty_label = ttk.Label(self.content_frame, text="You don't have any saved or submitted applications.")
            empty_label.pack(pady=50)
            
            start_btn = ttk.Button(self.content_frame, text="Start New Application", command=self.show_form_selection)
            start_btn.pack(pady=20)
            return
        
        # Create a table to display applications
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        columns = ("Application Type", "Status", "Date", "Reference ID", "Actions")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add sample data
        sample_apps = [
            ("Passport Application", "In Progress", "01/04/2025", "TEMP123456", "Continue"),
            ("Aadhaar Update", "Submitted", "28/03/2025", "AAD789456", "View"),
            ("PAN Application", "Rejected", "15/03/2025", "PAN456123", "Reapply")
        ]
        
        for app in sample_apps:
            tree.insert("", tk.END, values=app)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=20)
        
        new_app_btn = ttk.Button(button_frame, text="Start New Application", command=self.show_form_selection)
        new_app_btn.pack(side=tk.LEFT, padx=10)
    
    def show_track_status(self):
        self.clear_content()
        
        title_label = ttk.Label(self.content_frame, text="Track Application Status", style="Title.TLabel")
        title_label.pack(pady=20)
        
        search_frame = ttk.Frame(self.content_frame)
        search_frame.pack(pady=20)
        
        ttk.Label(search_frame, text="Application Reference Number:").pack(side=tk.LEFT, padx=5)
        
        ref_entry = ttk.Entry(search_frame, width=20)
        ref_entry.pack(side=tk.LEFT, padx=5)
        
        track_btn = ttk.Button(search_frame, text="Track", command=lambda: self.search_application(ref_entry.get()))
        track_btn.pack(side=tk.LEFT, padx=5)
    
    def search_application(self, ref_number):
        if not ref_number:
            messagebox.showwarning("Input Required", "Please enter an application reference number.")
            return
        
        # In a real app, this would search a database
        # For demo, showing a sample tracking page
        self.clear_content()
        
        title_label = ttk.Label(
            self.content_frame, 
            text=f"Status for Application: {ref_number}",
            style="Title.TLabel"
        )
        title_label.pack(pady=20)
        
        # Status timeline
        timeline_frame = ttk.LabelFrame(self.content_frame, text="Application Timeline")
        timeline_frame.pack(fill=tk.X, padx=50, pady=10)
        
        status_items = [
            ("Application Submitted", "01/04/2025 09:15 AM", "Completed"),
            ("Document Verification", "01/04/2025 02:30 PM", "Completed"),
            ("Application Processing", "02/04/2025 10:45 AM", "In Progress"),
            ("Approval", "", "Pending"),
            ("Dispatch", "", "Pending")
        ]
        
        for item, date, status in status_items:
            status_frame = ttk.Frame(timeline_frame)
            status_frame.pack(fill=tk.X, pady=5)
            
            if status == "Completed":
                status_icon = "✓"
                status_color = "green"
            elif status == "In Progress":
                status_icon = "➤"
                status_color = "blue"
            else:
                status_icon = "○"
                status_color = "gray"
            
            icon_label = ttk.Label(status_frame, text=status_icon, foreground=status_color, font=("Arial", 12, "bold"))
            icon_label.pack(side=tk.LEFT, padx=10)
            
            item_label = ttk.Label(status_frame, text=item, font=("Arial", 10, "bold"))
            item_label.pack(side=tk.LEFT, padx=10)
            
            date_label = ttk.Label(status_frame, text=date)
            date_label.pack(side=tk.RIGHT, padx=20)
        
        # Additional details
        details_frame = ttk.LabelFrame(self.content_frame, text="Application Details")
        details_frame.pack(fill=tk.X, padx=50, pady=20)
        
        details = [
            ("Application Type:", "Passport (Normal)"),
            ("Applicant Name:", "Test User"),
            ("Submission Date:", "01/04/2025"),
            ("Expected Completion:", "15/04/2025"),
            ("Current Status:", "Under Processing")
        ]
        
        for label, value in details:
            detail_frame = ttk.Frame(details_frame)
            detail_frame.pack(fill=tk.X, pady=5)
            
            label_widget = ttk.Label(detail_frame, text=label, width=20)
            label_widget.pack(side=tk.LEFT, padx=10)
            
            value_widget = ttk.Label(detail_frame, text=value)
            value_widget.pack(side=tk.LEFT, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=20)
        
        back_btn = ttk.Button(button_frame, text="Back", command=self.show_track_status)
        back_btn.pack(side=tk.LEFT, padx=10)
        
        download_btn = ttk.Button(button_frame, text="Download Receipt", command=self.dummy_function)
        download_btn.pack(side=tk.LEFT, padx=10)
    
    def show_help(self):
        self.clear_content()
        
        title_label = ttk.Label(self.content_frame, text="Help & Support", style="Title.TLabel")
        title_label.pack(pady=20)
        
        # FAQ section
        faq_frame = ttk.LabelFrame(self.content_frame, text="Frequently Asked Questions")
        faq_frame.pack(fill=tk.X, padx=50, pady=10)
        
        faqs = [
            ("How do I check my application status?", 
             "You can track your application status using the 'Track Status' option in the navigation menu."),
            ("What documents are required for passport application?", 
             "Passport applications require address proof, identity proof, birth certificate, and recent photographs."),
            ("How long does it take to process my application?", 
             "Processing times vary by application type. Passport: 7-30 days, Aadhar: 7-14 days, PAN: 7-15 days."),
            ("My application was rejected. What should I do?", 
             "Check the rejection reason in your status. Fix the issues and reapply through the 'My Applications' section.")
        ]
        
        for question, answer in faqs:
            faq_item = ttk.Frame(faq_frame)
            faq_item.pack(fill=tk.X, pady=10, padx=10)
            
            q_label = ttk.Label(faq_item, text=question, font=("Arial", 10, "bold"))
            q_label.pack(anchor=tk.W)
            
            a_label = ttk.Label(faq_item, text=answer, wraplength=700)
            a_label.pack(anchor=tk.W, padx=20, pady=5)
        
        # Contact section
        contact_frame = ttk.LabelFrame(self.content_frame, text="Contact Us")
        contact_frame.pack(fill=tk.X, padx=50, pady=20)
        
        contact_info = [
            ("Phone:", "1800-XXX-XXXX (Toll Free)"),
            ("Email:", "support@formfiller.gov.in"),
            ("Hours:", "Monday to Friday, 9:00 AM to 5:30 PM"),
            ("Address:", "Ministry of Electronics & Information Technology, Electronics Niketan, 6, CGO Complex, New Delhi - 110003")
        ]
        
        for label, value in contact_info:
            contact_item = ttk.Frame(contact_frame)
            contact_item.pack(fill=tk.X, pady=5)
            
            label_widget = ttk.Label(contact_item, text=label, width=10)
            label_widget.pack(side=tk.LEFT, padx=10)
            
            value_widget = ttk.Label(contact_item, text=value)
            value_widget.pack(side=tk.LEFT, padx=10)
        
        # Feedback form
        feedback_frame = ttk.LabelFrame(self.content_frame, text="Submit Feedback")
        feedback_frame.pack(fill=tk.X, padx=50, pady=20)
        
        feedback_label = ttk.Label(feedback_frame, text="We value your feedback. Please share your experience with our application:")
        feedback_label.pack(anchor=tk.W, padx=10, pady=10)
        
        feedback_text = tk.Text(feedback_frame, height=5, width=70)
        feedback_text.pack(padx=10, pady=5)
        
        submit_btn = ttk.Button(feedback_frame, text="Submit Feedback", command=self.dummy_function)
        submit_btn.pack(anchor=tk.E, padx=10, pady=10)
    
    def print_acknowledgement(self):
        messagebox.showinfo("Print", "Printing acknowledgement... (This is a simulation)")
    
    def logout(self):
        response = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if response:
            messagebox.showinfo("Logged Out", "You have been successfully logged out.")
            self.user_data = {}
            self.show_home()
    
    def dummy_function(self):
        messagebox.showinfo("Info", "This feature is not implemented in the demo.")
    
    def clear_content(self):
        # Clear all widgets from content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()


def main():
    root = tk.Tk()
    app = IndianFormFillerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()