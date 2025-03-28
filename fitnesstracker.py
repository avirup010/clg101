import sys
import sqlite3
from datetime import date, datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QDateEdit)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QDate

class FitnessTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FitnessPro Tracker")
        self.setGeometry(100, 100, 800, 600)
        
        # Setup database
        self.setup_database()
        
        # Main container
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Tab Widget for different tracking sections
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Workout Logging Tab
        workout_tab = QWidget()
        workout_layout = QVBoxLayout()
        workout_tab.setLayout(workout_layout)
        
        # Workout Input Section
        workout_input_layout = QHBoxLayout()
        workout_name = QLineEdit()
        workout_name.setPlaceholderText("Workout Name")
        workout_duration = QLineEdit()
        workout_duration.setPlaceholderText("Duration (minutes)")
        workout_calories = QLineEdit()
        workout_calories.setPlaceholderText("Calories Burned")
        
        add_workout_btn = QPushButton("Log Workout")
        add_workout_btn.clicked.connect(lambda: self.log_workout(
            workout_name.text(), 
            workout_duration.text(), 
            workout_calories.text()
        ))
        
        workout_input_layout.addWidget(workout_name)
        workout_input_layout.addWidget(workout_duration)
        workout_input_layout.addWidget(workout_calories)
        workout_input_layout.addWidget(add_workout_btn)
        
        workout_layout.addLayout(workout_input_layout)
        
        # Workout History Table
        self.workout_table = QTableWidget()
        self.workout_table.setColumnCount(4)
        self.workout_table.setHorizontalHeaderLabels(["Date", "Workout", "Duration", "Calories"])
        workout_layout.addWidget(self.workout_table)
        
        # Nutrition Logging Tab
        nutrition_tab = QWidget()
        nutrition_layout = QVBoxLayout()
        nutrition_tab.setLayout(nutrition_layout)
        
        # Nutrition Input Section
        nutrition_input_layout = QHBoxLayout()
        food_name = QLineEdit()
        food_name.setPlaceholderText("Food Item")
        calories = QLineEdit()
        calories.setPlaceholderText("Calories")
        
        add_food_btn = QPushButton("Log Meal")
        add_food_btn.clicked.connect(lambda: self.log_nutrition(
            food_name.text(), 
            calories.text()
        ))
        
        nutrition_input_layout.addWidget(food_name)
        nutrition_input_layout.addWidget(calories)
        nutrition_input_layout.addWidget(add_food_btn)
        
        nutrition_layout.addLayout(nutrition_input_layout)
        
        # Nutrition History Table
        self.nutrition_table = QTableWidget()
        self.nutrition_table.setColumnCount(3)
        self.nutrition_table.setHorizontalHeaderLabels(["Date", "Food Item", "Calories"])
        nutrition_layout.addWidget(self.nutrition_table)
        
        # Summary Section
        summary_layout = QHBoxLayout()
        self.total_calories_burned = QLabel("Calories Burned: 0")
        self.total_calories_consumed = QLabel("Calories Consumed: 0")
        summary_layout.addWidget(self.total_calories_burned)
        summary_layout.addWidget(self.total_calories_consumed)
        main_layout.addLayout(summary_layout)
        
        # Add tabs
        tab_widget.addTab(workout_tab, "Workout Tracking")
        tab_widget.addTab(nutrition_tab, "Nutrition Tracking")
        
        # Style the application
        self.setStyleSheet("""
        QWidget {
            background-color: #f0f4f8;
            font-family: 'Arial';
        }
        QLineEdit {
            padding: 8px;
            border: 1px solid #c0c0c0;
            border-radius: 10px;
            background-color: white;
        }
        QPushButton {
            background-color: #4a90e2;
            color: white;
            border-radius: 10px;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #357abd;
        }
        QTabWidget::pane {
            border-radius: 10px;
        }
        QTableWidget {
            background-color: white;
            border-radius: 10px;
        }
        """)
        
        # Load initial data
        self.load_workout_history()
        self.load_nutrition_history()
        self.update_summary()
    
    def setup_database(self):
        """Initialize SQLite database for tracking"""
        self.conn = sqlite3.connect('fitness_tracker.db')
        cursor = self.conn.cursor()
        
        # Create workout table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY,
                date TEXT,
                workout_name TEXT,
                duration INTEGER,
                calories INTEGER
            )
        ''')
        
        # Create nutrition table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nutrition (
                id INTEGER PRIMARY KEY,
                date TEXT,
                food_item TEXT,
                calories INTEGER
            )
        ''')
        
        self.conn.commit()
    
    def log_workout(self, workout_name, duration, calories):
        """Log a new workout"""
        try:
            duration = int(duration)
            calories = int(calories)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO workouts (date, workout_name, duration, calories)
                VALUES (?, ?, ?, ?)
            ''', (str(date.today()), workout_name, duration, calories))
            
            self.conn.commit()
            self.load_workout_history()
            self.update_summary()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for duration and calories.")
    
    def log_nutrition(self, food_name, calories):
        """Log a new nutrition entry"""
        try:
            calories = int(calories)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO nutrition (date, food_item, calories)
                VALUES (?, ?, ?)
            ''', (str(date.today()), food_name, calories))
            
            self.conn.commit()
            self.load_nutrition_history()
            self.update_summary()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for calories.")
    
    def load_workout_history(self):
        """Load and display workout history"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT date, workout_name, duration, calories FROM workouts')
        workouts = cursor.fetchall()
        
        self.workout_table.setRowCount(len(workouts))
        for row, (date, workout, duration, calories) in enumerate(workouts):
            self.workout_table.setItem(row, 0, QTableWidgetItem(date))
            self.workout_table.setItem(row, 1, QTableWidgetItem(workout))
            self.workout_table.setItem(row, 2, QTableWidgetItem(str(duration)))
            self.workout_table.setItem(row, 3, QTableWidgetItem(str(calories)))
    
    def load_nutrition_history(self):
        """Load and display nutrition history"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT date, food_item, calories FROM nutrition')
        nutrition_entries = cursor.fetchall()
        
        self.nutrition_table.setRowCount(len(nutrition_entries))
        for row, (date, food, calories) in enumerate(nutrition_entries):
            self.nutrition_table.setItem(row, 0, QTableWidgetItem(date))
            self.nutrition_table.setItem(row, 1, QTableWidgetItem(food))
            self.nutrition_table.setItem(row, 2, QTableWidgetItem(str(calories)))
    
    def update_summary(self):
        """Update calorie summary"""
        cursor = self.conn.cursor()
        
        # Total calories burned
        cursor.execute('SELECT SUM(calories) FROM workouts WHERE date = ?', (str(date.today()),))
        total_burned = cursor.fetchone()[0] or 0
        
        # Total calories consumed
        cursor.execute('SELECT SUM(calories) FROM nutrition WHERE date = ?', (str(date.today()),))
        total_consumed = cursor.fetchone()[0] or 0
        
        self.total_calories_burned.setText(f"Calories Burned: {total_burned}")
        self.total_calories_consumed.setText(f"Calories Consumed: {total_consumed}")
    
    def closeEvent(self, event):
        """Close database connection on app exit"""
        self.conn.close()

def main():
    app = QApplication(sys.argv)
    fitness_tracker = FitnessTracker()
    fitness_tracker.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()