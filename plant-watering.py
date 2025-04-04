import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QListWidget, QFormLayout, 
                             QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

# SQLite Database Setup
def init_db():
    try:
        conn = sqlite3.connect("plants.db")
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS plants 
                     (id INTEGER PRIMARY KEY, name TEXT, frequency INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS watering_log 
                     (id INTEGER PRIMARY KEY, plant_id INTEGER, date TEXT, 
                     FOREIGN KEY(plant_id) REFERENCES plants(id))''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

class PlantTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.setWindowTitle("Plant Watering Tracker")
            self.setGeometry(100, 100, 800, 600)  # Ensure it's on-screen
            
            # Make sure window is visible by removing opacity animations at startup
            self.setWindowOpacity(1.0)
            
            # Central widget with solid dark background (not glass-like)
            self.central_widget = QWidget(self)
            self.setCentralWidget(self.central_widget)
            self.central_widget.setStyleSheet("""
                background-color: #1A1A1A;  /* Darker background */
            """)
            self.layout = QVBoxLayout(self.central_widget)
            self.layout.setContentsMargins(20, 20, 20, 20)

            # Stylish font
            self.font = QFont("Segoe UI", 12)
            self.font.setWeight(QFont.Weight.Medium)  # Less bold for better readability
            QApplication.setFont(self.font)

            # Title
            self.title = QLabel("Plant Watering Tracker")
            self.title.setStyleSheet("font-size: 28px; color: #32CD32; background: transparent;")
            self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.title)

            # Main content area with scroll
            self.content_widget = QWidget()
            self.content_layout = QVBoxLayout(self.content_widget)
            self.scroll = QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setWidget(self.content_widget)
            self.scroll.setStyleSheet("background: #1A1A1A; border: none;")
            self.layout.addWidget(self.scroll)

            # Add plant form
            self.add_plant_frame = QFrame()
            self.add_plant_layout = QFormLayout(self.add_plant_frame)
            self.add_plant_frame.setStyleSheet("""
                background: #252525;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 15px;
            """)
            
            # Form label style
            form_label_style = "color: #32CD32; font-weight: bold;"
            
            plant_name_label = QLabel("Plant Name:")
            plant_name_label.setStyleSheet(form_label_style)
            
            freq_label = QLabel("Watering Frequency (days):")
            freq_label.setStyleSheet(form_label_style)
            
            self.plant_name_input = QLineEdit()
            self.plant_name_input.setStyleSheet("""
                border: 1px solid #444444;
                border-radius: 4px; 
                padding: 8px; 
                color: #FFFFFF; 
                background: #333333;
            """)
            
            self.frequency_input = QLineEdit()
            self.frequency_input.setStyleSheet("""
                border: 1px solid #444444;
                border-radius: 4px; 
                padding: 8px; 
                color: #FFFFFF; 
                background: #333333;
            """)
            
            self.add_button = QPushButton("Add Plant")
            self.add_button.setStyleSheet("""
                background: #225522;
                border: none;
                border-radius: 4px;
                padding: 10px;
                color: #FFFFFF;
                font-weight: bold;
            """)
            self.add_button.clicked.connect(self.add_plant)
            
            self.add_plant_layout.addRow(plant_name_label, self.plant_name_input)
            self.add_plant_layout.addRow(freq_label, self.frequency_input)
            self.add_plant_layout.addWidget(self.add_button)
            self.content_layout.addWidget(self.add_plant_frame)

            # Plant list
            self.plant_list = QListWidget()
            self.plant_list.setStyleSheet("""
                background: #252525;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 10px;
                color: #CCCCCC;
                margin-top: 15px;
            """)
            self.plant_list.itemClicked.connect(self.show_plant_details)
            self.content_layout.addWidget(self.plant_list)

            # Details panel (hidden initially)
            self.details_frame = QFrame()
            self.details_layout = QVBoxLayout(self.details_frame)
            self.details_frame.setStyleSheet("""
                background: #252525;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 15px;
                margin-top: 15px;
            """)
            self.details_frame.hide()
            
            self.plant_name_label = QLabel("")
            self.plant_name_label.setStyleSheet("color: #32CD32; font-size: 16px; font-weight: bold;")
            
            self.next_watering_label = QLabel("")
            self.next_watering_label.setStyleSheet("color: #CCCCCC; font-size: 14px;")
            
            self.water_button = QPushButton("Log Watering")
            self.water_button.setStyleSheet("""
                background: #225577;
                border: none;
                border-radius: 4px;
                padding: 10px;
                color: #FFFFFF;
                font-weight: bold;
                margin: 10px 0;
            """)
            self.water_button.clicked.connect(self.log_watering)
            
            self.history_label = QLabel("Watering History:")
            self.history_label.setStyleSheet("color: #32CD32; font-weight: bold; margin-top: 10px;")
            
            self.history_list = QListWidget()
            self.history_list.setStyleSheet("""
                background: #333333; 
                color: #CCCCCC; 
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
            """)
            
            self.details_layout.addWidget(self.plant_name_label)
            self.details_layout.addWidget(self.next_watering_label)
            self.details_layout.addWidget(self.water_button)
            self.details_layout.addWidget(self.history_label)
            self.details_layout.addWidget(self.history_list)
            self.content_layout.addWidget(self.details_frame)

            self.content_layout.addStretch()

            # Load plants and start reminder timer
            self.load_plants()
            self.timer = QTimer()
            self.timer.timeout.connect(self.check_reminders)
            self.timer.start(60000)  # Check every minute

        except Exception as e:
            print(f"Initialization error: {e}")

    def add_plant(self):
        name = self.plant_name_input.text()
        try:
            frequency = int(self.frequency_input.text())
            conn = sqlite3.connect("plants.db")
            c = conn.cursor()
            c.execute("INSERT INTO plants (name, frequency) VALUES (?, ?)", (name, frequency))
            conn.commit()
            conn.close()
            self.plant_name_input.clear()
            self.frequency_input.clear()
            self.load_plants()
        except ValueError:
            self.show_message("Please enter a valid number for frequency.")
        except sqlite3.Error as e:
            self.show_message(f"Database error: {e}")

    def load_plants(self):
        self.plant_list.clear()
        try:
            conn = sqlite3.connect("plants.db")
            c = conn.cursor()
            c.execute("SELECT id, name, frequency FROM plants")
            for row in c.fetchall():
                plant_id, name, frequency = row
                last_watered = self.get_last_watered(plant_id)
                next_watering = last_watered + timedelta(days=frequency) if last_watered else datetime.now()
                
                # Add a status indicator based on watering needs
                days_until = (next_watering.date() - datetime.now().date()).days
                if days_until <= 0:
                    status = "🔴"  # Needs water now
                elif days_until <= 2:
                    status = "🟠"  # Coming up soon
                else:
                    status = "🟢"  # Recently watered
                    
                item_text = f"{status} {name} - Next: {next_watering.strftime('%Y-%m-%d')}"
                self.plant_list.addItem(item_text)
            conn.close()
        except sqlite3.Error as e:
            self.show_message(f"Database error: {e}")

    def get_last_watered(self, plant_id):
        conn = sqlite3.connect("plants.db")
        c = conn.cursor()
        c.execute("SELECT date FROM watering_log WHERE plant_id = ? ORDER BY date DESC LIMIT 1", (plant_id,))
        result = c.fetchone()
        conn.close()
        return datetime.strptime(result[0], '%Y-%m-%d') if result else None

    def show_plant_details(self, item):
        # Extract the plant name by removing the emoji and splitting
        plant_name = item.text()[2:].split(" - ")[0]
        try:
            conn = sqlite3.connect("plants.db")
            c = conn.cursor()
            c.execute("SELECT id, frequency FROM plants WHERE name = ?", (plant_name,))
            plant_id, frequency = c.fetchone()
            
            last_watered = self.get_last_watered(plant_id)
            next_watering = last_watered + timedelta(days=frequency) if last_watered else datetime.now()
            
            # Calculate days until next watering
            days_until = (next_watering.date() - datetime.now().date()).days
            days_text = f"{days_until} days" if days_until > 0 else "Today!"
            
            self.plant_name_label.setText(f"Plant: {plant_name}")
            self.next_watering_label.setText(f"Next Watering: {next_watering.strftime('%Y-%m-%d')} ({days_text})")
            self.water_button.setProperty("plant_id", plant_id)

            # Load watering history
            self.history_list.clear()
            c.execute("SELECT date FROM watering_log WHERE plant_id = ? ORDER BY date DESC", (plant_id,))
            for row in c.fetchall():
                self.history_list.addItem(row[0])
            conn.close()

            # Show details panel without animation to avoid visibility issues
            self.details_frame.show()
            
        except sqlite3.Error as e:
            self.show_message(f"Database error: {e}")

    def log_watering(self):
        plant_id = self.water_button.property("plant_id")
        try:
            conn = sqlite3.connect("plants.db")
            c = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            c.execute("INSERT INTO watering_log (plant_id, date) VALUES (?, ?)", (plant_id, today))
            conn.commit()
            conn.close()
            self.load_plants()
            # Refreshing details after updating
            if self.plant_list.currentItem():
                self.show_plant_details(self.plant_list.currentItem())
            self.show_message("Watering logged successfully!")
        except sqlite3.Error as e:
            self.show_message(f"Database error: {e}")

    def check_reminders(self):
        try:
            conn = sqlite3.connect("plants.db")
            c = conn.cursor()
            c.execute("SELECT id, name, frequency FROM plants")
            today = datetime.now().date()
            for plant_id, name, frequency in c.fetchall():
                last_watered = self.get_last_watered(plant_id)
                next_watering = last_watered + timedelta(days=frequency) if last_watered else datetime.now()
                if next_watering.date() <= today:
                    self.show_message(f"Reminder: Time to water {name}!")
            conn.close()
        except sqlite3.Error as e:
            self.show_message(f"Database error: {e}")

    def show_message(self, text):
        msg = QLabel(text, self)
        msg.setStyleSheet("""
            background: #444444;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 10px;
            color: #FFFFFF;
        """)
        msg.setMinimumWidth(300)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Position in a visible area
        x = (self.width() - msg.width()) // 2
        msg.move(x, 100)
        msg.show()
        
        # Use a timer instead of animation to ensure visibility
        timer = QTimer(self)
        timer.timeout.connect(msg.deleteLater)
        timer.start(3000)  # Message disappears after 3 seconds

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        
        # Set darker application-wide style
        app.setStyle("Fusion")
        
        # Dark palette for the entire application
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(26, 26, 26))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(204, 204, 204))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(50, 50, 50))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(204, 204, 204))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(204, 204, 204))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(204, 204, 204))
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(35, 35, 35))
        
        app.setPalette(dark_palette)
        
        # Initialize database
        init_db()
        
        # Create and show the main window
        window = PlantTracker()
        window.show()
        
        # Extra debugging
        print(f"Window geometry: {window.geometry()}")
        print(f"Window is visible: {window.isVisible()}")
        print(f"Window opacity: {window.windowOpacity()}")
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"Application error: {e}")