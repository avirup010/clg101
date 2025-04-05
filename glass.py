import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint  # Added QPoint import
from PyQt6.QtGui import QColor, QPalette

class GlassWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("Glass UI App")
        self.setGeometry(100, 100, 400, 300)
        
        # Make window frameless and translucent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Glass-like background for the central widget
        self.central_widget.setStyleSheet("""
            background: rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        """)

        # Title label
        self.title_label = QLabel("Glass UI App", self)
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            background: transparent;
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Animated button
        self.button = QPushButton("Click Me", self)
        self.button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.3);
                border: none;
                border-radius: 10px;
                padding: 10px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.5);
            }
        """)
        self.button.clicked.connect(self.animate_button)
        self.layout.addWidget(self.button)

        # Response label (hidden initially)
        self.response_label = QLabel("", self)
        self.response_label.setStyleSheet("""
            font-size: 16px;
            color: white;
            background: transparent;
        """)
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.response_label.hide()
        self.layout.addWidget(self.response_label)

        # Add stretch to center content
        self.layout.addStretch()

        # Initial animation for window fade-in
        self.animate_window()

    def animate_window(self):
        # Fade-in animation for the entire window
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(1000)  # 1 second
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()

    def animate_button(self):
        # Show response label with animation
        self.response_label.setText("Button Clicked!")
        self.response_label.show()

        # Slide and fade animation for the response label
        self.anim = QPropertyAnimation(self.response_label, b"pos")
        self.anim.setDuration(500)  # 0.5 seconds
        self.anim.setStartValue(self.response_label.pos())
        self.anim.setEndValue(self.response_label.pos() + QPoint(0, -20))  # Now QPoint is defined
        self.anim.setEasingCurve(QEasingCurve.Type.OutBounce)
        self.anim.start()

        # Fade-in effect for the label
        self.fade_anim = QPropertyAnimation(self.response_label, b"windowOpacity")
        self.fade_anim.setDuration(500)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

    def mousePressEvent(self, event):
        # Allow dragging the frameless window
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        # Drag the window
        delta = event.globalPosition().toPoint() - self.old_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set a dark theme for better contrast with glass effect
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    app.setPalette(palette)

    window = GlassWindow()
    window.show()
    sys.exit(app.exec())