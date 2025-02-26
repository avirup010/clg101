import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QSlider, 
                             QLabel, QStyle, QFrame)
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QPen, QFont
import pygame
from pygame import mixer
import random
import time

class AudioData(QThread):
    data_updated = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.paused = True
        self.sample_rate = 44100
        self.buffer_size = 1024
        self.spectrum_data = np.zeros(self.buffer_size // 2)
        
        # Initialize pygame mixer
        pygame.init()
        mixer.init(frequency=self.sample_rate)
        
    def load_file(self, filename):
        try:
            mixer.music.load(filename)
            self.paused = False
            mixer.music.play()
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def toggle_playback(self):
        if mixer.music.get_busy():
            if self.paused:
                mixer.music.unpause()
            else:
                mixer.music.pause()
            self.paused = not self.paused
        else:
            mixer.music.play()
            self.paused = False
    
    def set_volume(self, volume):
        # Volume from 0.0 to 1.0
        mixer.music.set_volume(volume / 100.0)
    
    def run(self):
        while self.running:
            if mixer.music.get_busy() and not self.paused:
                # Generate spectrum data with smooth transitions
                target = np.abs(np.fft.rfft(np.random.rand(self.buffer_size) * 2 - 1))
                target = np.log10(target + 1) * 20  # Logarithmic scale for better visualization
                
                # Smooth transition
                self.spectrum_data = self.spectrum_data * 0.7 + target * 0.3
                self.data_updated.emit(self.spectrum_data)
            
            time.sleep(0.03)  # ~30 fps
    
    def stop(self):
        self.running = False
        mixer.music.stop()
        pygame.quit()
        self.wait()


class VisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 300)
        
        # Visualization properties
        self.spectrum_data = np.zeros(512)
        self.bars_count = 64
        self.bar_width = 8
        self.bar_spacing = 2
        self.animation_speed = 0.2
        self.visualization_mode = 'bars'  # 'bars', 'wave', 'circle'
        self.color_scheme = 'spectrum'    # 'spectrum', 'gradient', 'pulse'
        
        # Animation properties
        self.particles = []
        self.max_particles = 100
        
        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(20, 20, 30))
        self.setPalette(palette)
    
    def update_data(self, data):
        # Resample data to match our bar count
        if len(data) > self.bars_count:
            indices = np.linspace(0, len(data) - 1, self.bars_count, dtype=int)
            self.spectrum_data = data[indices]
        else:
            self.spectrum_data = data
        
        # Generate some particles for animation
        if random.random() > 0.7:
            self.add_particle()
        
        # Update particle positions
        for particle in self.particles[:]:
            particle['life'] -= 0.02
            particle['y'] += particle['speed']
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        self.update()
    
    def add_particle(self):
        if len(self.particles) < self.max_particles:
            self.particles.append({
                'x': random.randint(0, self.width()),
                'y': random.randint(0, self.height()),
                'size': random.randint(2, 6),
                'speed': random.uniform(0.5, 2.0),
                'life': 1.0,
                'color': QColor(
                    random.randint(150, 255),
                    random.randint(150, 255),
                    random.randint(200, 255),
                    random.randint(100, 200)
                )
            })
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw particles
        for particle in self.particles:
            painter.setPen(Qt.NoPen)
            painter.setBrush(particle['color'])
            size = particle['size'] * particle['life']
            painter.drawEllipse(
                int(particle['x'] - size/2), 
                int(particle['y'] - size/2),
                int(size), int(size)
            )
        
        # Draw visualization based on current mode
        if self.visualization_mode == 'bars':
            self.draw_bars(painter)
        elif self.visualization_mode == 'wave':
            self.draw_wave(painter)
        elif self.visualization_mode == 'circle':
            self.draw_circle(painter)
    
    def draw_bars(self, painter):
        width = self.width()
        height = self.height()
        bar_width = max(2, min((width - (self.bars_count * self.bar_spacing)) // self.bars_count, self.bar_width))
        
        # Calculate starting x position to center the bars
        start_x = (width - (self.bars_count * (bar_width + self.bar_spacing))) // 2
        
        for i, value in enumerate(self.spectrum_data):
            # Normalize the value (0-1) and apply to height
            normalized = min(1.0, value / 100)
            bar_height = int(normalized * height * 0.8)
            
            # Calculate position
            x = start_x + i * (bar_width + self.bar_spacing)
            y = height - bar_height
            
            # Create color gradient based on height
            if self.color_scheme == 'spectrum':
                hue = int(240 * (1 - normalized))  # Blue to Red
                color = QColor.fromHsv(hue, 240, 255)
            elif self.color_scheme == 'gradient':
                gradient = QLinearGradient(x, y, x, height)
                gradient.setColorAt(0, QColor(64, 224, 208))  # Turquoise
                gradient.setColorAt(1, QColor(148, 0, 211))   # Purple
                painter.setBrush(gradient)
                painter.setPen(Qt.NoPen)
            elif self.color_scheme == 'pulse':
                intensity = int(200 + 55 * normalized)
                color = QColor(0, intensity, intensity)
            
            if self.color_scheme != 'gradient':
                painter.setBrush(color)
                painter.setPen(Qt.NoPen)
            
            # Draw the bar
            painter.drawRoundedRect(x, y, bar_width, bar_height, 2, 2)
            
            # Add top highlight
            painter.setPen(QColor(255, 255, 255, 100))
            painter.drawLine(x, y, x + bar_width, y)
    
    def draw_wave(self, painter):
        width = self.width()
        height = self.height()
        center_y = height // 2
        
        # Create path for the wave
        points = []
        for i, value in enumerate(self.spectrum_data):
            normalized = min(1.0, value / 100)
            x = int((i / len(self.spectrum_data)) * width)
            y = int(center_y - (normalized * height * 0.4))
            points.append((x, y))
        
        # Draw the wave path
        painter.setPen(QPen(QColor(0, 200, 255, 200), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for i in range(len(points) - 1):
            painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        
        # Draw the mirrored wave
        painter.setPen(QPen(QColor(0, 150, 255, 150), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for i in range(len(points) - 1):
            mirror_y1 = 2 * center_y - points[i][1]
            mirror_y2 = 2 * center_y - points[i+1][1]
            painter.drawLine(points[i][0], mirror_y1, points[i+1][0], mirror_y2)
        
        # Draw horizontal center line
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1, Qt.DashLine))
        painter.drawLine(0, center_y, width, center_y)
    
    def draw_circle(self, painter):
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        max_radius = min(width, height) // 2 - 20
        
        # Draw outer circle
        painter.setPen(QPen(QColor(100, 100, 100, 50), 1))
        painter.drawEllipse(center_x - max_radius, center_y - max_radius, 
                           max_radius * 2, max_radius * 2)
        
        # Draw spectrum points
        angle_step = 2 * np.pi / len(self.spectrum_data)
        
        for i, value in enumerate(self.spectrum_data):
            normalized = min(1.0, value / 100)
            radius = int(max_radius * (0.2 + normalized * 0.8))
            angle = i * angle_step
            
            x = center_x + int(radius * np.cos(angle))
            y = center_y + int(radius * np.sin(angle))
            
            # Color based on angle and amplitude
            hue = int((i / len(self.spectrum_data)) * 360)
            saturation = 200 + int(normalized * 55)
            brightness = 200 + int(normalized * 55)
            color = QColor.fromHsv(hue, saturation, brightness)
            
            # Draw point
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            point_size = 2 + int(normalized * 6)
            painter.drawEllipse(x - point_size//2, y - point_size//2, point_size, point_size)
            
            # Connect to center with a line
            painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 40), 1))
            painter.drawLine(center_x, center_y, x, y)
            
            # Connect points
            if i > 0:
                prev_normalized = min(1.0, self.spectrum_data[i-1] / 100)
                prev_radius = int(max_radius * (0.2 + prev_normalized * 0.8))
                prev_angle = (i-1) * angle_step
                prev_x = center_x + int(prev_radius * np.cos(prev_angle))
                prev_y = center_y + int(prev_radius * np.sin(prev_angle))
                
                painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 100), 1))
                painter.drawLine(prev_x, prev_y, x, y)
    
    def change_visualization(self, mode):
        self.visualization_mode = mode
        self.update()
    
    def change_color_scheme(self, scheme):
        self.color_scheme = scheme
        self.update()
    
    def resizeEvent(self, event):
        # Recalculate bar width on resize
        width = self.width()
        self.bar_width = max(2, min((width - (self.bars_count * self.bar_spacing)) // self.bars_count, 12))
        super().resizeEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Audio Visualizer")
        self.setMinimumSize(800, 500)
        
        # Initialize the audio processing thread
        self.audio_thread = AudioData()
        self.audio_thread.data_updated.connect(self.update_visualizer)
        self.audio_thread.start()
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Create visualizer widget
        self.visualizer = VisualizerWidget()
        main_layout.addWidget(self.visualizer, 1)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Create controls
        controls_layout = QHBoxLayout()
        
        # File selection button
        self.open_button = QPushButton("Open Audio")
        self.open_button.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.open_button.clicked.connect(self.open_file)
        controls_layout.addWidget(self.open_button)
        
        # Play/Pause button
        self.play_button = QPushButton("Play")
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_button)
        
        # Volume control
        volume_layout = QVBoxLayout()
        volume_label = QLabel("Volume")
        volume_label.setAlignment(Qt.AlignCenter)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        controls_layout.addLayout(volume_layout)
        
        # Visualization mode selection
        viz_layout = QVBoxLayout()
        viz_label = QLabel("Visualization")
        viz_label.setAlignment(Qt.AlignCenter)
        viz_buttons_layout = QHBoxLayout()
        
        self.bars_button = QPushButton("Bars")
        self.bars_button.clicked.connect(lambda: self.visualizer.change_visualization('bars'))
        self.wave_button = QPushButton("Wave")
        self.wave_button.clicked.connect(lambda: self.visualizer.change_visualization('wave'))
        self.circle_button = QPushButton("Circle")
        self.circle_button.clicked.connect(lambda: self.visualizer.change_visualization('circle'))
        
        viz_buttons_layout.addWidget(self.bars_button)
        viz_buttons_layout.addWidget(self.wave_button)
        viz_buttons_layout.addWidget(self.circle_button)
        
        viz_layout.addWidget(viz_label)
        viz_layout.addLayout(viz_buttons_layout)
        controls_layout.addLayout(viz_layout)
        
        # Color scheme selection
        color_layout = QVBoxLayout()
        color_label = QLabel("Color Scheme")
        color_label.setAlignment(Qt.AlignCenter)
        color_buttons_layout = QHBoxLayout()
        
        self.spectrum_button = QPushButton("Spectrum")
        self.spectrum_button.clicked.connect(lambda: self.visualizer.change_color_scheme('spectrum'))
        self.gradient_button = QPushButton("Gradient")
        self.gradient_button.clicked.connect(lambda: self.visualizer.change_color_scheme('gradient'))
        self.pulse_button = QPushButton("Pulse")
        self.pulse_button.clicked.connect(lambda: self.visualizer.change_color_scheme('pulse'))
        
        color_buttons_layout.addWidget(self.spectrum_button)
        color_buttons_layout.addWidget(self.gradient_button)
        color_buttons_layout.addWidget(self.pulse_button)
        
        color_layout.addWidget(color_label)
        color_layout.addLayout(color_buttons_layout)
        controls_layout.addLayout(color_layout)
        
        main_layout.addLayout(controls_layout)
        
        # Set the central widget
        self.setCentralWidget(main_widget)
        
        # Set up a timer for smooth animations
        self.timer = QTimer()
        self.timer.timeout.connect(self.visualizer.update)
        self.timer.start(33)  # ~30 fps
        
        # Apply some styling
        self.apply_styles()
    
    def apply_styles(self):
        # Apply some basic styling to make UI more attractive
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QWidget {
                background-color: #1a1a2e;
                color: #e6e6e6;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #0f3460;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #16437a;
            }
            QPushButton:pressed {
                background-color: #1e5993;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #333333;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #16437a;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #1e5993;
            }
            QLabel {
                color: #e6e6e6;
            }
        """)
    
    def update_visualizer(self, data):
        self.visualizer.update_data(data)
    
    def open_file(self):
        file_dialog = QFileDialog()
        filename, _ = file_dialog.getOpenFileName(
            self, "Open Audio File", "", 
            "Audio Files (*.mp3 *.wav *.ogg *.flac);;All Files (*)"
        )
        
        if filename:
            if self.audio_thread.load_file(filename):
                # Update UI
                self.play_button.setText("Pause")
                self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
    
    def toggle_playback(self):
        self.audio_thread.toggle_playback()
        
        if self.audio_thread.paused:
            self.play_button.setText("Play")
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.play_button.setText("Pause")
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
    
    def set_volume(self, value):
        self.audio_thread.set_volume(value)
    
    def closeEvent(self, event):
        # Properly clean up resources
        self.timer.stop()
        self.audio_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
