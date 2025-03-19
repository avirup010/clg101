import cv2
import face_recognition
import numpy as np
import os
import pickle
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

class FaceRecognitionSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize variables
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_current_frame = True
        self.current_image = None
        self.video_capture = None
        self.is_webcam_active = False
        self.dataset_folder = "face_dataset"
        self.encodings_file = "face_encodings.pkl"
        
        # Create dataset folder if it doesn't exist
        if not os.path.exists(self.dataset_folder):
            os.makedirs(self.dataset_folder)
        
        # Load existing encodings if available
        self.load_encodings()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.recognition_tab = ttk.Frame(self.notebook)
        self.dataset_tab = ttk.Frame(self.notebook)
        self.training_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.recognition_tab, text="Face Recognition")
        self.notebook.add(self.dataset_tab, text="Dataset Management")
        self.notebook.add(self.training_tab, text="Training")
        
        # Set up each tab
        self.setup_recognition_tab()
        self.setup_dataset_tab()
        self.setup_training_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_recognition_tab(self):
        # Split into two frames: controls and display
        controls_frame = ttk.Frame(self.recognition_tab, padding=10)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        display_frame = ttk.Frame(self.recognition_tab, padding=10)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Controls
        ttk.Label(controls_frame, text="Recognition Controls", font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))
        
        # Webcam controls
        webcam_frame = ttk.LabelFrame(controls_frame, text="Webcam", padding=10)
        webcam_frame.pack(fill=tk.X, pady=10)
        
        self.webcam_btn = ttk.Button(webcam_frame, text="Start Webcam", command=self.toggle_webcam)
        self.webcam_btn.pack(fill=tk.X, pady=5)
        
        ttk.Button(webcam_frame, text="Take Screenshot", command=self.take_screenshot).pack(fill=tk.X, pady=5)
        
        # Image controls
        image_frame = ttk.LabelFrame(controls_frame, text="Image Recognition", padding=10)
        image_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(image_frame, text="Load Image", command=self.load_image).pack(fill=tk.X, pady=5)
        ttk.Button(image_frame, text="Recognize Faces", command=self.recognize_faces_in_image).pack(fill=tk.X, pady=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(controls_frame, text="Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(settings_frame, text="Recognition Tolerance:").pack(anchor=tk.W)
        self.tolerance_var = tk.DoubleVar(value=0.6)
        tolerance_scale = ttk.Scale(settings_frame, from_=0.3, to=0.9, variable=self.tolerance_var, orient=tk.HORIZONTAL)
        tolerance_scale.pack(fill=tk.X, pady=5)
        ttk.Label(settings_frame, textvariable=tk.StringVar(value="Lower = More strict, Higher = More permissive")).pack()
        
        # Display area
        ttk.Label(display_frame, text="Recognition Display", font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))
        
        # Canvas for image/video display
        self.canvas = tk.Canvas(display_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Recognition info
        self.info_text = tk.Text(display_frame, height=5, wrap=tk.WORD)
        self.info_text.pack(fill=tk.X, pady=10)
        self.info_text.insert(tk.END, "Recognition information will appear here.")
        self.info_text.config(state=tk.DISABLED)
    
    def setup_dataset_tab(self):
        # Split into two frames: controls and display
        controls_frame = ttk.Frame(self.dataset_tab, padding=10)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        display_frame = ttk.Frame(self.dataset_tab, padding=10)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Controls
        ttk.Label(controls_frame, text="Dataset Controls", font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))
        
        # Add person frame
        add_frame = ttk.LabelFrame(controls_frame, text="Add Person", padding=10)
        add_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(add_frame, text="Person Name:").pack(anchor=tk.W, pady=(0, 5))
        self.person_name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.person_name_var).pack(fill=tk.X, pady=5)
        
        ttk.Label(add_frame, text="Image Source:").pack(anchor=tk.W, pady=(5, 0))
        self.image_source_var = tk.StringVar(value="webcam")
        ttk.Radiobutton(add_frame, text="Webcam", variable=self.image_source_var, value="webcam").pack(anchor=tk.W)
        ttk.Radiobutton(add_frame, text="File", variable=self.image_source_var, value="file").pack(anchor=tk.W)
        
        buttons_frame = ttk.Frame(add_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(buttons_frame, text="Capture/Select", command=self.add_person_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Add Multiple Images", command=self.add_multiple_images).pack(side=tk.LEFT)
        
        # Manage dataset frame
        manage_frame = ttk.LabelFrame(controls_frame, text="Manage Dataset", padding=10)
        manage_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(manage_frame, text="View Dataset", command=self.view_dataset).pack(fill=tk.X, pady=5)
        ttk.Button(manage_frame, text="Remove Person", command=self.remove_person).pack(fill=tk.X, pady=5)
        
        # Display area
        ttk.Label(display_frame, text="Dataset Preview", font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))
        
        # Treeview for dataset display
        self.dataset_tree = ttk.Treeview(display_frame, columns=("name", "images"), show="headings")
        self.dataset_tree.heading("name", text="Person Name")
        self.dataset_tree.heading("images", text="Number of Images")
        self.dataset_tree.column("name", width=150)
        self.dataset_tree.column("images", width=150)
        self.dataset_tree.pack(fill=tk.BOTH, expand=True)
        
        # Refresh the dataset view
        self.view_dataset()
    
    def setup_training_tab(self):
        # Center content
        main_frame = ttk.Frame(self.training_tab, padding=20)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Training controls
        ttk.Label(main_frame, text="Model Training", font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))
        
        # Info text
        info_text = """Training creates face encodings from all images in your dataset.
This allows the system to recognize faces more quickly.
It's recommended to train after adding or removing images."""
        
        ttk.Label(main_frame, text=info_text, wraplength=500).pack(pady=20)
        
        # Stats
        stats_frame = ttk.LabelFrame(main_frame, text="Dataset Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=20)
        
        self.people_count_var = tk.StringVar(value="People: 0")
        self.images_count_var = tk.StringVar(value="Images: 0")
        self.last_trained_var = tk.StringVar(value="Last trained: Never")
        
        ttk.Label(stats_frame, textvariable=self.people_count_var).pack(anchor=tk.W)
        ttk.Label(stats_frame, textvariable=self.images_count_var).pack(anchor=tk.W)
        ttk.Label(stats_frame, textvariable=self.last_trained_var).pack(anchor=tk.W)
        
        # Train button
        ttk.Button(main_frame, text="Train Face Recognition Model", 
                  command=self.train_model, style="Accent.TButton").pack(pady=20)
        
        # Update stats
        self.update_training_stats()
    
    def load_encodings(self):
        if os.path.exists(self.encodings_file):
            try:
                with open(self.encodings_file, "rb") as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data["encodings"]
                    self.known_face_names = data["names"]
                self.status_var.set(f"Loaded {len(self.known_face_encodings)} face encodings")
            except Exception as e:
                self.status_var.set(f"Error loading encodings: {str(e)}")
    
    def save_encodings(self):
        try:
            with open(self.encodings_file, "wb") as f:
                data = {"encodings": self.known_face_encodings, "names": self.known_face_names}
                pickle.dump(data, f)
            self.status_var.set(f"Saved {len(self.known_face_encodings)} face encodings")
        except Exception as e:
            self.status_var.set(f"Error saving encodings: {str(e)}")
    
    def toggle_webcam(self):
        if self.is_webcam_active:
            self.stop_webcam()
            self.webcam_btn.config(text="Start Webcam")
        else:
            self.start_webcam()
            self.webcam_btn.config(text="Stop Webcam")
    
    def start_webcam(self):
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            messagebox.showerror("Error", "Could not open webcam")
            return
        
        self.is_webcam_active = True
        self.update_webcam()
        self.status_var.set("Webcam active")
    
    def stop_webcam(self):
        self.is_webcam_active = False
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
        self.status_var.set("Webcam stopped")
    
    def update_webcam(self):
        if not self.is_webcam_active:
            return
        
        # Get frame from webcam
        ret, frame = self.video_capture.read()
        if not ret:
            self.stop_webcam()
            return
        
        # Only process every other frame to save time
        if self.process_current_frame:
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Find faces
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
            
            self.face_names = []
            for face_encoding in self.face_encodings:
                # See if the face is a match for known faces
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, 
                                                        tolerance=self.tolerance_var.get())
                name = "Unknown"
                
                # Use the distance to find the best match
                if len(self.known_face_encodings) > 0:
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = 1 - face_distances[best_match_index]
                        name = f"{name} ({confidence:.2%})"
                
                self.face_names.append(name)
        
        self.process_current_frame = not self.process_current_frame
        
        # Display results
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since we scaled down the image
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Draw box and label
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)
        
        # Convert to RGB for tkinter
        self.current_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.display_image(self.current_image)
        
        # Update recognition info
        self.update_recognition_info()
        
        # Continue updating
        self.root.after(10, self.update_webcam)
    
    def take_screenshot(self):
        if self.current_image is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.jpg"
            cv2.imwrite(filename, cv2.cvtColor(self.current_image, cv2.COLOR_RGB2BGR))
            self.status_var.set(f"Screenshot saved as {filename}")
        else:
            messagebox.showerror("Error", "No image to save")
    
    def load_image(self):
        filename = filedialog.askopenfilename(filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")
        ])
        
        if filename:
            try:
                # Load image
                image = cv2.imread(filename)
                if image is None:
                    raise ValueError("Could not load image")
                
                # Convert to RGB and display
                self.current_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.display_image(self.current_image)
                self.status_var.set(f"Loaded image: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def recognize_faces_in_image(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        
        # Get a copy of the current image
        image = self.current_image.copy()
        
        # Find faces
        rgb_image = image  # Already in RGB format
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for known faces
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, 
                                                    tolerance=self.tolerance_var.get())
            name = "Unknown"
            
            # Use the distance to find the best match
            if len(self.known_face_encodings) > 0:
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    confidence = 1 - face_distances[best_match_index]
                    name = f"{name} ({confidence:.2%})"
            
            face_names.append(name)
        
        # Display results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Draw box and label
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(image, name, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)
        
        # Display the result
        self.current_image = image
        self.display_image(image)
        
        # Update recognition info
        self.face_locations = face_locations
        self.face_names = face_names
        self.update_recognition_info()
        
        self.status_var.set(f"Recognized {len(face_locations)} faces")
    
    def display_image(self, image):
        # Get canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:  # Not initialized yet
            canvas_width = 640
            canvas_height = 480
        
        # Resize image to fit canvas while preserving aspect ratio
        height, width = image.shape[:2]
        scale = min(canvas_width / width, canvas_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        resized_image = cv2.resize(image, (new_width, new_height))
        
        # Convert to PhotoImage
        photo_image = ImageTk.PhotoImage(image=Image.fromarray(resized_image))
        
        # Update canvas
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.create_image(new_width // 2, new_height // 2, image=photo_image)
        self.canvas.image = photo_image  # Keep a reference
    
    def update_recognition_info(self):
        # Update info text
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        if len(self.face_locations) == 0:
            self.info_text.insert(tk.END, "No faces detected.")
        else:
            self.info_text.insert(tk.END, f"Detected {len(self.face_locations)} faces:\n")
            for name in self.face_names:
                self.info_text.insert(tk.END, f"- {name}\n")
        
        self.info_text.config(state=tk.DISABLED)
    
    def add_person_image(self):
        name = self.person_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a person name")
            return
        
        if self.image_source_var.get() == "webcam":
            if self.current_image is None:
                messagebox.showerror("Error", "No webcam image available")
                return
            
            # Use current frame from webcam
            image = self.current_image
        else:
            # Get image from file
            filename = filedialog.askopenfilename(filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp")
            ])
            
            if not filename:
                return
            
            image = cv2.imread(filename)
            if image is None:
                messagebox.showerror("Error", "Could not load image")
                return
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Create directory for person if it doesn't exist
        person_dir = os.path.join(self.dataset_folder, name)
        if not os.path.exists(person_dir):
            os.makedirs(person_dir)
        
        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(person_dir, f"{timestamp}.jpg")
        cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        
        self.status_var.set(f"Added image for {name}")
        messagebox.showinfo("Success", f"Image added to dataset for {name}")
        
        # Refresh dataset view
        self.view_dataset()
    
    def add_multiple_images(self):
        name = self.person_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a person name")
            return
        
        # Let user select multiple image files
        filenames = filedialog.askopenfilenames(filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp")
        ])
        
        if not filenames:
            return
        
        # Create directory for person if it doesn't exist
        person_dir = os.path.join(self.dataset_folder, name)
        if not os.path.exists(person_dir):
            os.makedirs(person_dir)
        
        # Save each image
        count = 0
        for filename in filenames:
            try:
                image = cv2.imread(filename)
                if image is None:
                    continue
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{count}"
                image_path = os.path.join(person_dir, f"{timestamp}.jpg")
                cv2.imwrite(image_path, image)
                count += 1
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
        
        self.status_var.set(f"Added {count} images for {name}")
        messagebox.showinfo("Success", f"Added {count} images to dataset for {name}")
        
        # Refresh dataset view
        self.view_dataset()
    
    def view_dataset(self):
        # Clear the treeview
        for item in self.dataset_tree.get_children():
            self.dataset_tree.delete(item)
        
        # Get list of people in dataset
        if not os.path.exists(self.dataset_folder):
            return
        
        people = [d for d in os.listdir(self.dataset_folder) 
                 if os.path.isdir(os.path.join(self.dataset_folder, d))]
        
        # Add to treeview
        for person in people:
            person_dir = os.path.join(self.dataset_folder, person)
            images = [f for f in os.listdir(person_dir) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            
            self.dataset_tree.insert("", tk.END, values=(person, len(images)))
        
        # Update stats
        self.update_training_stats()
    
    def remove_person(self):
        selected_items = self.dataset_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No person selected")
            return
        
        # Get selected person name
        person = self.dataset_tree.item(selected_items[0], "values")[0]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", f"Remove {person} from dataset?"):
            return
        
        # Delete directory
        person_dir = os.path.join(self.dataset_folder, person)
        try:
            # Delete all files in directory
            for file in os.listdir(person_dir):
                os.remove(os.path.join(person_dir, file))
            # Delete directory
            os.rmdir(person_dir)
            
            self.status_var.set(f"Removed {person} from dataset")
            messagebox.showinfo("Success", f"Removed {person} from dataset")
            
            # Refresh dataset view
            self.view_dataset()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove: {str(e)}")
    
    def update_training_stats(self):
        people_count = 0
        images_count = 0
        
        if os.path.exists(self.dataset_folder):
            people = [d for d in os.listdir(self.dataset_folder) 
                     if os.path.isdir(os.path.join(self.dataset_folder, d))]
            people_count = len(people)
            
            for person in people:
                person_dir = os.path.join(self.dataset_folder, person)
                images = [f for f in os.listdir(person_dir) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
                images_count += len(images)
        
        self.people_count_var.set(f"People: {people_count}")
        self.images_count_var.set(f"Images: {images_count}")
        
        if os.path.exists(self.encodings_file):
            mod_time = os.path.getmtime(self.encodings_file)
            mod_time_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
            self.last_trained_var.set(f"Last trained: {mod_time_str}")
        else:
            self.last_trained_var.set("Last trained: Never")
    
    def train_model(self):
        if not os.path.exists(self.dataset_folder):
            messagebox.showerror("Error", "Dataset folder does not exist")
            return
        
        people = [d for d in os.listdir(self.dataset_folder) 
                 if os.path.isdir(os.path.join(self.dataset_folder, d))]
        
        if not people:
            messagebox.showerror("Error", "No people in dataset")
            return
        
        # Ask for confirmation
        images_count = 0
        for person in people:
            person_dir = os.path.join(self.dataset_folder, person)
            images = [f for f in os.listdir(person_dir) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            images_count += len(images)
        
        if not messagebox.askyesno("Confirm", 
                                  f"Train model with {len(people)} people and {images_count} images?\nThis may take some time."):
            return
        
        # Show progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Training Progress")
        progress_window.geometry("300x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Training face recognition model...").pack(pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=images_count)
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        
        status_var = tk.StringVar(value="Starting...")
        status_label = ttk.Label(progress_window, textvariable=status_var)
        status_label.pack(pady=10)
        
        # Reset encodings
        self.known_face_encodings = []
        self.known_face_names = []
        
        # Process each person in a separate thread
        def training_thread():
            processed = 0
            for person in people:
                person_dir = os.path.join(self.dataset_folder, person)
                image_files = [f for f in os.listdir(person_dir) 
                              if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
                
                for image_file in image_files:
                    image_path = os.path.join(person_dir, image_file)
                    
                    # Update progress
                    progress_var.set(processed)
                    status_var.set(f"Processing {person}: {image_file}")
                    
                    try:
                        # Load image
                        image = face_recognition.load_image_file(image_path)
                        
                        # Find face encodings (using the first face found)
                        face_encodings = face_recognition.face_encodings(image)
                        
                        if face_encodings:
                            # Add encoding to dataset
                            self.known_face_encodings.append(face_encodings[0])
                            self.known_face_names.append(person)
                    except Exception as e:
                        print(f"Error processing {image_path}: {str(e)}")
                    
                    processed += 1
            
            # Save encodings
            self.save_encodings()
            
            # Update stats
            self.update_training_stats()
            
            # Close progress window
            progress_window.destroy()
            messagebox.showinfo("Success", f"Training complete! Processed {processed} images.")
        
        # Start training in a separate thread
        import threading
        threading.Thread(target=training_thread, daemon=True).start()
    
    def on_closing(self):
        # Stop webcam if active
        if self.is_webcam_active:
            self.stop_webcam()
        
        # Close the application
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FaceRecognitionSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()