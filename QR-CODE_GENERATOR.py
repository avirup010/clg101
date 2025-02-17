import sys
import os
import qrcode
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                            QFileDialog, QFrame, QColorDialog, QSlider)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PyQt5.QtGui import QPixmap, QColor, QPainter, QBrush, QIcon

class QRCodeGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern QR Code Generator")
        self.setMinimumSize(600, 500)
        
        # Color palette
        self.colors = {
            'primary': '#6200EE',         # Deep Purple - primary color
            'primary_variant': '#3700B3', # Dark Purple - for hover states
            'secondary': '#03DAC6',       # Teal - secondary color
            'secondary_variant': '#018786', # Dark Teal - for hover states
            'background': '#F7F7F7',      # Off-white - main background
            'surface': '#FFFFFF',         # White - card backgrounds
            'error': '#B00020',           # Red - error states
            'success': '#4CAF50',         # Green - success states
            'success_variant': '#388E3C', # Dark Green - hover state
            'on_primary': '#FFFFFF',      # White - text on primary color
            'on_secondary': '#000000',    # Black - text on secondary color
            'on_background': '#333333',   # Dark Gray - text on background
            'on_surface': '#333333',      # Dark Gray - text on surface
            'border': '#E0E0E0'           # Light Gray - borders
        }
        
        # Set application style
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['on_background']};
            }}
        """)
        
        # Set up the central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Try to set window icon if available
        try:
            self.setWindowIcon(QIcon("icon.png"))
        except:
            pass  # Ignore if icon file is not available
        
        # Title with animation
        self.title_label = QLabel("QR Code Generator")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {self.colors['primary']};")
        main_layout.addWidget(self.title_label)
        
        # Input section
        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        input_frame.setStyleSheet(f"#inputFrame {{ border-radius: 10px; background-color: {self.colors['surface']}; border: 1px solid {self.colors['border']}; }}")
        input_layout = QVBoxLayout(input_frame)
        
        # Text input
        text_layout = QHBoxLayout()
        text_label = QLabel("Enter text or URL:")
        text_label.setStyleSheet("font-size: 14px;")
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("https://example.com")
        self.text_input.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {self.colors['primary']};
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.colors['primary_variant']};
            }}
        """)
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.text_input)
        input_layout.addLayout(text_layout)
        
        # Color selection
        color_layout = QHBoxLayout()
        color_label = QLabel("QR Code Colors:")
        color_label.setStyleSheet("font-size: 14px;")
        
        self.fg_color_btn = QPushButton("Foreground")
        self.fg_color_btn.setStyleSheet(f"""
            background-color: #000000;
            color: #ffffff;
            border-radius: 5px;
            padding: 5px;
        """)
        self.fg_color_btn.clicked.connect(lambda: self.choose_color('fg'))
        self.fg_color = QColor(0, 0, 0)
        
        self.bg_color_btn = QPushButton("Background")
        self.bg_color_btn.setStyleSheet(f"""
            background-color: #FFFFFF;
            color: #000000;
            border-radius: 5px;
            padding: 5px;
            border: 1px solid {self.colors['border']};
        """)
        self.bg_color_btn.clicked.connect(lambda: self.choose_color('bg'))
        self.bg_color = QColor(255, 255, 255)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.fg_color_btn)
        color_layout.addWidget(self.bg_color_btn)
        input_layout.addLayout(color_layout)
        
        # Size slider
        size_layout = QHBoxLayout()
        size_label = QLabel("QR Code Size:")
        size_label.setStyleSheet("font-size: 14px;")
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(1)
        self.size_slider.setMaximum(10)
        self.size_slider.setValue(5)
        self.size_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {self.colors['border']};
                background: {self.colors['surface']};
                height: 10px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {self.colors['secondary']};
                border: 1px solid {self.colors['secondary_variant']};
                width: 18px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 9px;
            }}
        """)
        
        self.size_value_label = QLabel("Size: 5")
        self.size_slider.valueChanged.connect(self.update_size_label)
        
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(self.size_value_label)
        input_layout.addLayout(size_layout)
        
        main_layout.addWidget(input_frame)
        
        # Button section
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("Generate QR Code")
        self.generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['primary']};
                color: {self.colors['on_primary']};
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.colors['primary_variant']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['primary_variant']};
                padding-top: 12px;
                padding-bottom: 8px;
            }}
        """)
        self.generate_btn.clicked.connect(self.generate_qr)
        
        self.save_btn = QPushButton("Save QR Code")
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['success']};
                color: {self.colors['on_primary']};
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.colors['success_variant']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['success_variant']};
                padding-top: 12px;
                padding-bottom: 8px;
            }}
            QPushButton:disabled {{
                background-color: #BBBBBB;
                color: #666666;
            }}
        """)
        self.save_btn.clicked.connect(self.save_qr)
        self.save_btn.setEnabled(False)
        
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.save_btn)
        main_layout.addLayout(button_layout)
        
        # QR Code display area
        self.qr_frame = QFrame()
        self.qr_frame.setObjectName("qrFrame")
        self.qr_frame.setStyleSheet(f"#qrFrame {{ border-radius: 10px; background-color: {self.colors['surface']}; border: 1px solid {self.colors['border']}; }}")
        qr_layout = QVBoxLayout(self.qr_frame)
        
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setText("Your QR code will appear here")
        self.qr_label.setStyleSheet("font-size: 16px; color: #757575;")
        qr_layout.addWidget(self.qr_label)
        
        main_layout.addWidget(self.qr_frame)
        
        # Initialize animations
        self.setup_animations()
        
        # Show the window
        self.show()
        
        # Start intro animation
        QTimer.singleShot(100, self.start_intro_animation)
    
    def setup_animations(self):
        # Title animation
        self.title_animation = QPropertyAnimation(self.title_label, b"geometry")
        self.title_animation.setDuration(800)
        self.title_animation.setEasingCurve(QEasingCurve.OutBack)
    
    def start_intro_animation(self):
        # Animate title
        start_rect = self.title_label.geometry()
        self.title_animation.setStartValue(QRect(start_rect.x(), start_rect.y() - 50, start_rect.width(), start_rect.height()))
        self.title_animation.setEndValue(start_rect)
        self.title_animation.start()
        
        # Animate other elements with delayed start
        for i, widget in enumerate([self.qr_frame, self.generate_btn, self.save_btn]):
            animation = QPropertyAnimation(widget, b"geometry")
            animation.setDuration(600)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            
            start_rect = widget.geometry()
            animation.setStartValue(QRect(start_rect.x() + 50, start_rect.y(), start_rect.width(), start_rect.height()))
            animation.setEndValue(start_rect)
            
            # Delayed start
            QTimer.singleShot(200 + i * 100, animation.start)
    
    def update_size_label(self):
        self.size_value_label.setText(f"Size: {self.size_slider.value()}")
    
    def choose_color(self, color_type):
        dialog = QColorDialog(self)
        if color_type == 'fg':
            current_color = self.fg_color
        else:
            current_color = self.bg_color
            
        color = dialog.getColor(current_color, self, "Choose Color")
        
        if color.isValid():
            if color_type == 'fg':
                self.fg_color = color
                self.fg_color_btn.setStyleSheet(f"""
                    background-color: {color.name()};
                    color: {'#ffffff' if color.lightness() < 128 else '#000000'};
                    border-radius: 5px;
                    padding: 5px;
                """)
            else:
                self.bg_color = color
                self.bg_color_btn.setStyleSheet(f"""
                    background-color: {color.name()};
                    color: {'#ffffff' if color.lightness() < 128 else '#000000'};
                    border-radius: 5px;
                    padding: 5px;
                    border: 1px solid {self.colors['border']};
                """)
    
    def generate_qr(self):
        text = self.text_input.text().strip()
        if not text:
            self.qr_label.setText("Please enter text or URL first!")
            self.qr_label.setStyleSheet(f"font-size: 16px; color: {self.colors['error']};")
            self.save_btn.setEnabled(False)
            return
        
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            # Create image with proper colors
            img = qr.make_image(fill_color=self.fg_color.name(), back_color=self.bg_color.name())
            
            # Convert to QPixmap for display
            img_path = "temp_qr.png"
            img.save(img_path)
            
            # Scale pixmap according to slider value
            pixmap = QPixmap(img_path)
            size_factor = self.size_slider.value() * 30  # Scale factor
            pixmap = pixmap.scaled(size_factor, size_factor, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Animate the label
            self.qr_label.setPixmap(pixmap)
            self.qr_label.setStyleSheet("")  # Reset any error styling
            
            # Enable save button
            self.save_btn.setEnabled(True)
            
            # Animate QR code appearance
            self.animate_qr_appearance()
            
        except Exception as e:
            self.qr_label.setText(f"Error generating QR code: {str(e)}")
            self.qr_label.setStyleSheet(f"font-size: 16px; color: {self.colors['error']};")
            self.save_btn.setEnabled(False)
    
    def animate_qr_appearance(self):
        # Create a zoom-in effect for the QR code
        animation = QPropertyAnimation(self.qr_label, b"geometry")
        animation.setDuration(500)
        animation.setEasingCurve(QEasingCurve.OutBack)
        
        start_rect = self.qr_label.geometry()
        center_x = start_rect.x() + start_rect.width() / 2
        center_y = start_rect.y() + start_rect.height() / 2
        
        # Start smaller from the center
        small_rect = QRect(
            int(center_x - start_rect.width() * 0.4),
            int(center_y - start_rect.height() * 0.4),
            int(start_rect.width() * 0.8),
            int(start_rect.height() * 0.8)
        )
        
        animation.setStartValue(small_rect)
        animation.setEndValue(start_rect)
        animation.start()
    
    def save_qr(self):
        if self.qr_label.pixmap():
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save QR Code",
                os.path.expanduser("~/qrcode.png"),
                "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
            )
            
            if filename:
                self.qr_label.pixmap().save(filename)
                
                # Show saved animation
                original_text = self.save_btn.text()
                self.save_btn.setText("Saved!")
                original_style = self.save_btn.styleSheet()
                
                # Change to a more vibrant success color
                self.save_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #8BC34A;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px;
                        font-size: 16px;
                        font-weight: bold;
                    }}
                """)
                
                # Reset button after delay
                QTimer.singleShot(1500, lambda: self.save_btn.setText(original_text))
                QTimer.singleShot(1500, lambda: self.save_btn.setStyleSheet(original_style))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QRCodeGenerator()
    sys.exit(app.exec_())
