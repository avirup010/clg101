"""
YouTube Video Downloader with Modern UI
======================================

This program provides a beautiful graphical user interface for downloading YouTube videos
using the yt-dlp library. It features a modern material design with smooth animations.

Features:
- Download videos in MP4 format or extract audio as MP3
- Progress tracking with real-time speed display
- Download history with ability to open destination folders
- Support for both videos and playlists
- Automatic FFmpeg detection with fallback options

Requirements:
- Python 3.6+
- PyQt5 (pip install PyQt5)
- yt-dlp (pip install yt-dlp)
- FFmpeg (optional, but required for MP3 extraction and best quality MP4)

How to install FFmpeg:
- Windows: Download from ffmpeg.org, extract, and add bin folder to PATH
- macOS: Using Homebrew: brew install ffmpeg
- Linux: sudo apt install ffmpeg (Ubuntu/Debian) or sudo dnf install ffmpeg (Fedora)

How the program works:
1. The main window is created using PyQt5 with a dark theme and material design elements
2. When a download is initiated, a worker thread is created to handle the download process
3. The worker uses yt-dlp to fetch video information and download the content
4. Progress updates are sent from the worker to the main thread via Qt signals
5. Download history is maintained in a list widget for easy access to completed downloads
6. The program checks for FFmpeg availability and adjusts options accordingly

Key Components:
- MainWindow: The main application window and UI
- DownloadWorker: Handles the actual download process in a separate thread
- RoundedButton: Custom styled button with rounded corners
- AnimatedFrame: Frame with animation capabilities (for future enhancements)

Author: Avirup Ghosh
Version: 1.0.0
"""
import sys
import os
import threading
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                             QComboBox, QProgressBar, QFileDialog, QMessageBox,
                             QListWidget, QListWidgetItem, QFrame)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QObject, QSize, QUrl
from PyQt5.QtGui import QIcon, QColor, QPalette, QFont, QMovie, QDesktopServices
import yt_dlp

# Constants
TITLE = "YT Downloader Pro"
VERSION = "1.0.0"
DEFAULT_DOWNLOAD_PATH = str(Path.home() / "Downloads" / "YT Downloader Pro")
DARK_COLOR = "#2c2f33"
ACCENT_COLOR = "#5865f2"
LIGHT_TEXT = "#ffffff"
SECONDARY_COLOR = "#36393f"
ERROR_COLOR = "#ed4245"
SUCCESS_COLOR = "#57f287"

# Create default download directory if it doesn't exist
if not os.path.exists(DEFAULT_DOWNLOAD_PATH):
    os.makedirs(DEFAULT_DOWNLOAD_PATH)

def is_ffmpeg_installed():
    """Check if ffmpeg is installed and available in PATH"""
    try:
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=False
        )
        return True
    except FileNotFoundError:
        return False

class DownloadWorker(QObject):
    progress_update = pyqtSignal(float, str)
    download_complete = pyqtSignal(bool, str)
    
    def __init__(self, url, save_path, format_option):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.format_option = format_option
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes'] > 0:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            else:
                percent = 0
                
            speed = d.get('speed', 0)
            if speed:
                speed_str = f"{speed/1024/1024:.1f} MB/s"
            else:
                speed_str = "calculating..."
                
            self.progress_update.emit(percent, speed_str)
        
        if d['status'] == 'finished':
            self.progress_update.emit(100, "Processing...")
            
    def run(self):
        try:
            # Check if ffmpeg is installed when needed
            if self.format_option == "MP3 (Audio)" or self.format_option == "MP4 (Video + Audio)":
                if not is_ffmpeg_installed():
                    self.download_complete.emit(False, "Error: ffmpeg is not installed. It's required for audio extraction and video merging.")
                    return
            
            # Base options
            ydl_opts = {
                'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }
            
            if self.format_option == "MP3 (Audio)":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            elif self.format_option == "MP4 (Video + Audio)":
                ydl_opts.update({
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': 'mp4',
                })
            else:  # Fallback to best available format that doesn't require merging
                ydl_opts.update({
                    'format': 'best',
                })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            
            self.download_complete.emit(True, "Download completed successfully!")
        except Exception as e:
            self.download_complete.emit(False, f"Error: {str(e)}")

class RoundedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("roundedButton")
        
class AnimatedFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        
    def fadeIn(self, duration=250):
        self.setVisible(False)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(duration)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.setVisible(True)
        self.opacity_anim.start()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowTitle(f"{TITLE} v{VERSION}")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {DARK_COLOR};
                color: {LIGHT_TEXT};
                font-family: 'Segoe UI', Arial;
            }}
            
            QLineEdit, QComboBox {{
                background-color: {SECONDARY_COLOR};
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
                color: {LIGHT_TEXT};
                font-size: 14px;
                selection-background-color: {ACCENT_COLOR};
            }}
            
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {ACCENT_COLOR};
            }}
            
            QComboBox::drop-down {{
                border: 0;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: url(down-arrow.png);
            }}
            
            QListWidget {{
                background-color: {SECONDARY_COLOR};
                border-radius: 4px;
                padding: 8px;
                outline: none;
            }}
            
            QListWidget::item {{
                padding: 8px;
                margin: 2px 0;
                border-radius: 4px;
            }}
            
            QListWidget::item:selected {{
                background-color: {ACCENT_COLOR};
            }}
            
            QProgressBar {{
                background-color: {SECONDARY_COLOR};
                border-radius: 4px;
                height: 12px;
                text-align: center;
            }}
            
            QProgressBar::chunk {{
                background-color: {ACCENT_COLOR};
                border-radius: 4px;
            }}
            
            #roundedButton {{
                background-color: {ACCENT_COLOR};
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }}
            
            #roundedButton:hover {{
                background-color: #4752c4;
            }}
            
            #roundedButton:pressed {{
                background-color: #3b45a0;
            }}
            
            QLabel {{
                font-size: 14px;
            }}
            
            QLabel#titleLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {LIGHT_TEXT};
            }}
            
            QLabel#statusLabel {{
                font-size: 12px;
                color: #aaa;
            }}
            
            QFrame#separator {{
                background-color: #444;
                max-height: 1px;
            }}
        """)
        
        # Central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)
        
        # Title
        self.title_label = QLabel(TITLE)
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)
        
        # Input section
        self.input_frame = QFrame()
        self.input_layout = QVBoxLayout(self.input_frame)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        
        # URL input
        self.url_layout = QHBoxLayout()
        self.url_label = QLabel("YouTube URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube video or playlist URL here")
        self.url_layout.addWidget(self.url_label)
        self.url_layout.addWidget(self.url_input)
        self.input_layout.addLayout(self.url_layout)
        
        # Format and save location
        self.options_layout = QHBoxLayout()
        
        self.format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4 (Video + Audio)", "MP3 (Audio)", "Best Available (No ffmpeg needed)"])
        self.format_combo.setFixedWidth(250)
        
        self.location_label = QLabel("Save to:")
        self.location_input = QLineEdit(DEFAULT_DOWNLOAD_PATH)
        self.location_input.setReadOnly(True)
        self.browse_button = RoundedButton("Browse")
        self.browse_button.setFixedWidth(100)
        self.browse_button.clicked.connect(self.browse_location)
        
        self.options_layout.addWidget(self.format_label)
        self.options_layout.addWidget(self.format_combo)
        self.options_layout.addSpacing(20)
        self.options_layout.addWidget(self.location_label)
        self.options_layout.addWidget(self.location_input)
        self.options_layout.addWidget(self.browse_button)
        
        self.input_layout.addLayout(self.options_layout)
        self.main_layout.addWidget(self.input_frame)
        
        # FFMPEG warning if not installed
        self.ffmpeg_warning = QLabel("")
        self.ffmpeg_warning.setStyleSheet(f"color: {ERROR_COLOR}; font-size: 12px;")
        self.ffmpeg_warning.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.ffmpeg_warning)
        
        # Check ffmpeg on startup
        self.check_ffmpeg()
        
        # Download button
        self.download_button = RoundedButton("Download")
        self.download_button.setFixedHeight(50)
        self.download_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.download_button.clicked.connect(self.start_download)
        self.main_layout.addWidget(self.download_button, alignment=Qt.AlignCenter)
        
        # Separator
        self.separator = QFrame()
        self.separator.setObjectName("separator")
        self.separator.setFrameShape(QFrame.HLine)
        self.main_layout.addWidget(self.separator)
        
        # Progress section
        self.progress_frame = QFrame()
        self.progress_layout = QVBoxLayout(self.progress_frame)
        self.progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setFormat("%p% Complete")
        
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        self.progress_layout.addWidget(self.progress_bar)
        self.progress_layout.addWidget(self.status_label)
        
        self.main_layout.addWidget(self.progress_frame)
        
        # History section
        self.history_label = QLabel("Download History")
        self.history_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.main_layout.addWidget(self.history_label)
        
        self.history_list = QListWidget()
        self.history_list.setSelectionMode(QListWidget.SingleSelection)
        self.history_list.itemDoubleClicked.connect(self.open_download_folder)
        self.main_layout.addWidget(self.history_list)
        
        # Status bar
        self.statusBar().showMessage(f"{TITLE} v{VERSION} | Ready")
        
        # Initialize download thread variables
        self.download_thread = None
        self.worker = None
    
    def check_ffmpeg(self):
        if not is_ffmpeg_installed():
            self.ffmpeg_warning.setText("⚠️ FFmpeg not found! Some formats will be unavailable. Please install FFmpeg for full functionality.")
        else:
            self.ffmpeg_warning.setText("")
            
    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Location", self.location_input.text())
        if folder:
            self.location_input.setText(folder)
            
    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a valid YouTube URL")
            return
        
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            self.url_input.setText(url)
        
        self.download_button.setEnabled(False)
        self.progress_bar.setValue(0)
        
        save_path = self.location_input.text()
        format_option = self.format_combo.currentText()
        
        # Create and start the download thread
        self.worker = DownloadWorker(url, save_path, format_option)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.download_complete.connect(self.download_finished)
        
        self.download_thread = threading.Thread(target=self.worker.run)
        self.download_thread.daemon = True
        self.download_thread.start()
        
        self.status_label.setText("Downloading... Please wait")
        self.statusBar().showMessage("Download in progress...")
        
    def update_progress(self, percent, speed_str):
        self.progress_bar.setValue(int(percent))
        self.status_label.setText(f"Downloading... {speed_str}")
        
    def download_finished(self, success, message):
        self.download_button.setEnabled(True)
        self.status_label.setText(message)
        self.statusBar().showMessage(message)
        
        if success:
            self.add_to_history(self.url_input.text(), self.format_combo.currentText(), self.location_input.text())
            self.url_input.clear()
        else:
            QMessageBox.warning(self, "Download Error", message)
            
    def add_to_history(self, url, format_type, save_path):
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', url)
        except:
            title = url
            
        item = QListWidgetItem(f"{title} ({format_type})")
        item.setData(Qt.UserRole, save_path)
        self.history_list.insertItem(0, item)
        
    def open_download_folder(self, item):
        path = item.data(Qt.UserRole)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

def main():
    # Create the application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()