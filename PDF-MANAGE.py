"""PDF-MANAGE is a PyQt6-based PDF Manager that provides a tabbed interface for merging, splitting, watermarking, and compressing PDFs.
It uses PyMuPDF (fitz) for handling PDF operations and features a modern UI with buttons, sliders, progress bars, and drag-and-drop support. 
The interface follows a light-themed design with QSS styling and allows users to interact with PDFs seamlessly. 
The code is structured with object-oriented principles, ensuring modularity and ease of maintenance."""
import sys
import os
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, QListWidget,
                             QSlider, QLineEdit, QColorDialog, QComboBox, QMessageBox,
                             QProgressBar, QSpinBox)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QFont, QColor, QDragEnterEvent, QDropEvent

class PDFManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Main window properties
        self.setWindowTitle("Modern PDF Manager")
        self.setMinimumSize(900, 600)
        
        # Center the window
        self.center_window()
        
        # Set app style
        self.set_style()
        
        # Initialize variables
        self.current_files = []
        self.watermark_text = ""
        self.watermark_color = QColor(128, 128, 128, 128)  # Semi-transparent gray
        
        # Create UI
        self.create_ui()
        
        # Setup drag and drop
        self.setAcceptDrops(True)
    
    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
    
    def set_style(self):
        # Set the font
        app_font = QFont("Oswald", 10)
        QApplication.setFont(app_font)
        
        # Set global stylesheet
        style = """
        QMainWindow {
            background-color: #E2A8E8;
        }
        QTabWidget::pane {
            border: 1px solid #48259E;
            background-color: white;
            border-radius: 5px;
        }
        QTabBar::tab {
            background-color: #699ED7;
            padding: 8px 20px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: blue;
            border-bottom: 2px solid #1976D2;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        QPushButton:disabled {
            background-color: #BDBDBD;
        }
        QListWidget {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            padding: 5px;
        }
        QSlider::groove:horizontal {
            border: 1px solid #999999;
            height: 8px;
            background: #E0E0E0;
            margin: 2px 0;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #2196F3;
            width: 18px;
            height: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        QLineEdit {
            padding: 6px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        QComboBox {
            padding: 6px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        QSpinBox {
            padding: 6px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        QProgressBar {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: #f5f5f5;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #2196F3;
            border-radius: 3px;
        }
        """
        self.setStyleSheet(style)
    
    def create_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.create_merge_tab()
        self.create_split_tab()
        self.create_watermark_tab()
        self.create_compress_tab()
        
        # Add tabs to tab widget
        main_layout.addWidget(self.tabs)
        
        # Set central widget
        self.setCentralWidget(central_widget)
    
    def create_merge_tab(self):
        # Create tab widget
        merge_tab = QWidget()
        layout = QVBoxLayout(merge_tab)
        
        # Create header
        header = QLabel("Merge PDF Files")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Create file list
        self.merge_file_list = QListWidget()
        self.merge_file_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        layout.addWidget(self.merge_file_list)
        
        # Create buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add files button
        add_button = QPushButton("Add Files")
        add_button.clicked.connect(self.add_merge_files)
        buttons_layout.addWidget(add_button)
        
        # Remove selected button
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_merge_files)
        buttons_layout.addWidget(remove_button)
        
        # Clear all button
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_merge_files)
        buttons_layout.addWidget(clear_button)
        
        # Add buttons layout to main layout
        layout.addLayout(buttons_layout)
        
        # Create merge button
        merge_button = QPushButton("Merge Files")
        merge_button.clicked.connect(self.merge_pdfs)
        layout.addWidget(merge_button)
        
        # Add progress bar
        self.merge_progress = QProgressBar()
        self.merge_progress.setVisible(False)
        layout.addWidget(self.merge_progress)
        
        # Add tab to tabs
        self.tabs.addTab(merge_tab, "Merge")
    
    def create_split_tab(self):
        # Create tab widget
        split_tab = QWidget()
        layout = QVBoxLayout(split_tab)
        
        # Create header
        header = QLabel("Split PDF File")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Create file selection layout
        file_layout = QHBoxLayout()
        
        # File path
        self.split_file_path = QLineEdit()
        self.split_file_path.setPlaceholderText("Select a PDF file to split...")
        self.split_file_path.setReadOnly(True)
        file_layout.addWidget(self.split_file_path, 3)
        
        # Browse button
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.select_split_file)
        file_layout.addWidget(browse_button, 1)
        
        # Add file layout to main layout
        layout.addLayout(file_layout)
        
        # Split options
        options_layout = QHBoxLayout()
        
        # Split method
        self.split_method = QComboBox()
        self.split_method.addItems(["Split by page range", "Extract single page", "Split into individual pages"])
        self.split_method.currentIndexChanged.connect(self.update_split_options)
        options_layout.addWidget(QLabel("Split Method:"))
        options_layout.addWidget(self.split_method)
        
        # Page input
        self.page_input = QLineEdit()
        self.page_input.setPlaceholderText("e.g. 1-5,8,11-13")
        options_layout.addWidget(QLabel("Pages:"))
        options_layout.addWidget(self.page_input)
        
        # Add options layout to main layout
        layout.addLayout(options_layout)
        
        # Create split button
        split_button = QPushButton("Split PDF")
        split_button.clicked.connect(self.split_pdf)
        layout.addWidget(split_button)
        
        # Add progress bar
        self.split_progress = QProgressBar()
        self.split_progress.setVisible(False)
        layout.addWidget(self.split_progress)
        
        # Add tab to tabs
        self.tabs.addTab(split_tab, "Split")
    
    def create_watermark_tab(self):
        # Create tab widget
        watermark_tab = QWidget()
        layout = QVBoxLayout(watermark_tab)
        
        # Create header
        header = QLabel("Add Watermark to PDF")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Create file selection layout
        file_layout = QHBoxLayout()
        
        # File path
        self.watermark_file_path = QLineEdit()
        self.watermark_file_path.setPlaceholderText("Select a PDF file to watermark...")
        self.watermark_file_path.setReadOnly(True)
        file_layout.addWidget(self.watermark_file_path, 3)
        
        # Browse button
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.select_watermark_file)
        file_layout.addWidget(browse_button, 1)
        
        # Add file layout to main layout
        layout.addLayout(file_layout)
        
        # Watermark text input
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Watermark Text:"))
        self.watermark_text_input = QLineEdit()
        self.watermark_text_input.setPlaceholderText("Enter watermark text...")
        text_layout.addWidget(self.watermark_text_input)
        layout.addLayout(text_layout)
        
        # Color selection
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Text Color:"))
        self.color_button = QPushButton()
        self.color_button.setFixedSize(30, 30)
        self.update_color_button()
        self.color_button.clicked.connect(self.select_watermark_color)
        color_layout.addWidget(self.color_button)
        
        # Opacity slider
        color_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(128)
        self.opacity_slider.valueChanged.connect(self.update_watermark_opacity)
        color_layout.addWidget(self.opacity_slider)
        
        layout.addLayout(color_layout)
        
        # Font size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Font Size:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(10, 100)
        self.font_size.setValue(40)
        size_layout.addWidget(self.font_size)
        layout.addLayout(size_layout)
        
        # Create watermark button
        watermark_button = QPushButton("Add Watermark")
        watermark_button.clicked.connect(self.add_watermark)
        layout.addWidget(watermark_button)
        
        # Add progress bar
        self.watermark_progress = QProgressBar()
        self.watermark_progress.setVisible(False)
        layout.addWidget(self.watermark_progress)
        
        # Add tab to tabs
        self.tabs.addTab(watermark_tab, "Watermark")
    
    def create_compress_tab(self):
        # Create tab widget
        compress_tab = QWidget()
        layout = QVBoxLayout(compress_tab)
        
        # Create header
        header = QLabel("Compress PDF File")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Create file selection layout
        file_layout = QHBoxLayout()
        
        # File path
        self.compress_file_path = QLineEdit()
        self.compress_file_path.setPlaceholderText("Select a PDF file to compress...")
        self.compress_file_path.setReadOnly(True)
        file_layout.addWidget(self.compress_file_path, 3)
        
        # Browse button
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.select_compress_file)
        file_layout.addWidget(browse_button, 1)
        
        # Add file layout to main layout
        layout.addLayout(file_layout)
        
        # Compression level
        compression_layout = QHBoxLayout()
        compression_layout.addWidget(QLabel("Compression Level:"))
        self.compression_level = QSlider(Qt.Orientation.Horizontal)
        self.compression_level.setRange(0, 4)
        self.compression_level.setValue(2)
        self.compression_level.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.compression_level.setTickInterval(1)
        compression_layout.addWidget(self.compression_level)
        
        # Add compression labels
        level_labels = QHBoxLayout()
        level_labels.addWidget(QLabel("Low"))
        level_labels.addStretch()
        level_labels.addWidget(QLabel("Medium"))
        level_labels.addStretch()
        level_labels.addWidget(QLabel("High"))
        
        layout.addLayout(compression_layout)
        layout.addLayout(level_labels)
        
        # Create compress button
        compress_button = QPushButton("Compress PDF")
        compress_button.clicked.connect(self.compress_pdf)
        layout.addWidget(compress_button)
        
        # Add progress bar
        self.compress_progress = QProgressBar()
        self.compress_progress.setVisible(False)
        layout.addWidget(self.compress_progress)
        
        # Add file info
        self.file_info = QLabel()
        layout.addWidget(self.file_info)
        
        # Add tab to tabs
        self.tabs.addTab(compress_tab, "Compress")
    
    # --- MERGE FUNCTIONS ---
    
    def add_merge_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        for file in files:
            self.merge_file_list.addItem(file)
    
    def remove_merge_files(self):
        for item in self.merge_file_list.selectedItems():
            self.merge_file_list.takeItem(self.merge_file_list.row(item))
    
    def clear_merge_files(self):
        self.merge_file_list.clear()
    
    def merge_pdfs(self):
        # Get files from list
        files = [self.merge_file_list.item(i).text() for i in range(self.merge_file_list.count())]
        
        if len(files) < 2:
            QMessageBox.warning(self, "Warning", "Please add at least two PDF files to merge.")
            return
        
        # Get output file
        output_file, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
        
        if not output_file:
            return
        
        # Ensure .pdf extension
        if not output_file.lower().endswith('.pdf'):
            output_file += '.pdf'
        
        # Show progress bar
        self.merge_progress.setVisible(True)
        self.merge_progress.setValue(0)
        
        try:
            # Create PDF merger
            merged_pdf = fitz.open()
            
            # Set progress maximum
            self.merge_progress.setMaximum(len(files))
            
            # Add each PDF to the merger
            for i, file in enumerate(files):
                pdf = fitz.open(file)
                merged_pdf.insert_pdf(pdf)
                
                # Update progress
                self.merge_progress.setValue(i + 1)
                QApplication.processEvents()
            
            # Save merged PDF
            merged_pdf.save(output_file)
            merged_pdf.close()
            
            # Show success message
            QMessageBox.information(self, "Success", "PDF files merged successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while merging PDF files: {str(e)}")
        
        finally:
            # Hide progress bar
            self.merge_progress.setVisible(False)
    
    # --- SPLIT FUNCTIONS ---
    
    def select_split_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file:
            self.split_file_path.setText(file)
    
    def update_split_options(self):
        method = self.split_method.currentIndex()
        if method == 0:  # Split by page range
            self.page_input.setPlaceholderText("e.g. 1-5,8,11-13")
            self.page_input.setEnabled(True)
        elif method == 1:  # Extract single page
            self.page_input.setPlaceholderText("e.g. 5")
            self.page_input.setEnabled(True)
        else:  # Split into individual pages
            self.page_input.clear()
            self.page_input.setEnabled(False)
    
    def split_pdf(self):
        # Get input file
        input_file = self.split_file_path.text()
        
        if not input_file:
            QMessageBox.warning(self, "Warning", "Please select a PDF file to split.")
            return
        
        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        
        if not output_dir:
            return
        
        # Show progress bar
        self.split_progress.setVisible(True)
        self.split_progress.setValue(0)
        
        try:
            # Open PDF file
            pdf = fitz.open(input_file)
            
            # Get method and pages
            method = self.split_method.currentIndex()
            
            if method == 0:  # Split by page range
                page_ranges = self.parse_page_ranges(self.page_input.text(), pdf.page_count)
                if not page_ranges:
                    QMessageBox.warning(self, "Warning", "Invalid page range format.")
                    self.split_progress.setVisible(False)
                    return
                
                # Set progress maximum
                self.split_progress.setMaximum(len(page_ranges))
                
                # Split PDF by page ranges
                for i, (start, end) in enumerate(page_ranges):
                    new_pdf = fitz.open()
                    new_pdf.insert_pdf(pdf, from_page=start - 1, to_page=end - 1)
                    output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}_pages_{start}-{end}.pdf")
                    new_pdf.save(output_file)
                    new_pdf.close()
                    
                    # Update progress
                    self.split_progress.setValue(i + 1)
                    QApplication.processEvents()
                
            elif method == 1:  # Extract single page
                try:
                    page_num = int(self.page_input.text().strip())
                    if page_num < 1 or page_num > pdf.page_count:
                        raise ValueError("Page number out of range")
                    
                    # Set progress maximum
                    self.split_progress.setMaximum(1)
                    
                    # Extract single page
                    new_pdf = fitz.open()
                    new_pdf.insert_pdf(pdf, from_page=page_num - 1, to_page=page_num - 1)
                    output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}_page_{page_num}.pdf")
                    new_pdf.save(output_file)
                    new_pdf.close()
                    
                    # Update progress
                    self.split_progress.setValue(1)
                    
                except ValueError:
                    QMessageBox.warning(self, "Warning", "Invalid page number.")
                    self.split_progress.setVisible(False)
                    return
                
            else:  # Split into individual pages
                # Set progress maximum
                self.split_progress.setMaximum(pdf.page_count)
                
                # Split PDF into individual pages
                for page_num in range(pdf.page_count):
                    new_pdf = fitz.open()
                    new_pdf.insert_pdf(pdf, from_page=page_num, to_page=page_num)
                    output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}_page_{page_num + 1}.pdf")
                    new_pdf.save(output_file)
                    new_pdf.close()
                    
                    # Update progress
                    self.split_progress.setValue(page_num + 1)
                    QApplication.processEvents()
            
            # Close PDF
            pdf.close()
            
            # Show success message
            QMessageBox.information(self, "Success", "PDF file split successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while splitting PDF file: {str(e)}")
        
        finally:
            # Hide progress bar
            self.split_progress.setVisible(False)
    
    def parse_page_ranges(self, text, max_pages):
        if not text.strip():
            return None
        
        ranges = []
        for part in text.split(','):
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    if start < 1 or end > max_pages or start > end:
                        return None
                    ranges.append((start, end))
                except ValueError:
                    return None
            else:
                try:
                    page = int(part)
                    if page < 1 or page > max_pages:
                        return None
                    ranges.append((page, page))
                except ValueError:
                    return None
        
        return ranges
    
    # --- WATERMARK FUNCTIONS ---
    
    def select_watermark_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file:
            self.watermark_file_path.setText(file)
    
    def update_color_button(self):
        pixmap = QIcon().pixmap(QSize(20, 20))
        pixmap.fill(self.watermark_color)
        self.color_button.setIcon(QIcon(pixmap))
    
    def select_watermark_color(self):
        color = QColorDialog.getColor(self.watermark_color, self, "Select Watermark Color", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            self.watermark_color = color
            self.opacity_slider.setValue(color.alpha())
            self.update_color_button()
    
    def update_watermark_opacity(self, value):
        self.watermark_color.setAlpha(value)
        self.update_color_button()
    
    def add_watermark(self):
        # Get input file
        input_file = self.watermark_file_path.text()
        
        if not input_file:
            QMessageBox.warning(self, "Warning", "Please select a PDF file to watermark.")
            return
        
        # Get watermark text
        watermark_text = self.watermark_text_input.text()
        
        if not watermark_text:
            QMessageBox.warning(self, "Warning", "Please enter watermark text.")
            return
        
        # Get output file
        output_file, _ = QFileDialog.getSaveFileName(self, "Save Watermarked PDF", "", "PDF Files (*.pdf)")
        
        if not output_file:
            return
        
        # Ensure .pdf extension
        if not output_file.lower().endswith('.pdf'):
            output_file += '.pdf'
        
        # Show progress bar
        self.watermark_progress.setVisible(True)
        self.watermark_progress.setValue(0)
        
        try:
            # Open PDF file
            pdf = fitz.open(input_file)
            
            # Set progress maximum
            self.watermark_progress.setMaximum(pdf.page_count)
            
            # Get font size and color
            font_size = self.font_size.value()
            text_color = (self.watermark_color.red() / 255, 
                         self.watermark_color.green() / 255, 
                         self.watermark_color.blue() / 255)
            alpha = self.watermark_color.alpha() / 255
            
            # Add watermark to each page
            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                
                # Calculate center position
                rect = page.rect
                x = rect.width / 2
                y = rect.height / 2
                
                # Create watermark text
                page.insert_text((x, y), watermark_text,
                               fontsize=font_size,
                               fontname="helv",
                               rotate=45,
                               color=text_color,
                               alpha=alpha,
                               align=fitz.TEXT_ALIGN_CENTER)
                
                # Update progress
                self.watermark_progress.setValue(page_num + 1)
                QApplication.processEvents()
            
            # Save watermarked PDF
            pdf.save(output_file)
            pdf.close()
            
            # Show success message
            QMessageBox.information(self, "Success", "Watermark added successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while adding watermark: {str(e)}")
        
        finally:
            # Hide progress bar
            self.watermark_progress.setVisible(False)
    
    # --- COMPRESS FUNCTIONS ---
    
    def select_compress_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file:
            self.compress_file_path.setText(file)
            self.update_file_info(file)
    
    def update_file_info(self, file_path):
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_mb = size / (1024 * 1024)
            self.file_info.setText(f"Original file size: {size_mb:.2f} MB")
        else:
            self.file_info.clear()
    
    def compress_pdf(self):
        # Get input file
        input_file = self.compress_file_path.text()
        
        if not input_file:
            QMessageBox.warning(self, "Warning", "Please select a PDF file to compress.")
            return
        
        # Get compression level
        level = self.compression_level.value()
        
        # Get output file
        output_file, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", "", "PDF Files (*.pdf)")
        
        if not output_file:
            return
        
        # Ensure .pdf extension
        if not output_file.lower().endswith('.pdf'):
            output_file += '.pdf'
        
        # Show progress bar
        self.compress_progress.setVisible(True)
        self.compress_progress.setValue(0)
        
        try:
            # Open PDF file
            pdf = fitz.open(input_file)
            
            # Set progress maximum
            self.compress_progress.setMaximum(pdf.page_count)
            
            # Set compression parameters based on level
            if level == 0:  # Lowest compression
                params = {
                    "deflate": True,
                    "garbage": 0,
                    "clean": False,
                    "linear": False
                }
            elif level == 1:
                params = {
                    "deflate": True,
                    "garbage": 1,
                    "clean": False,
                    "linear": False
                }
            elif level == 2:  # Medium compression (default)
                params = {
                    "deflate": True,
                    "garbage": 2,
                    "clean": True,
                    "linear": False
                }
            elif level == 3:
                params = {
                    "deflate": True,
                    "garbage": 3,
                    "clean": True,
                    "linear": True
                }
            else:  # Highest compression
                params = {
                    "deflate": True,
                    "garbage": 4,
                    "clean": True,
                    "linear": True
                }
            
            # Save compressed PDF
            pdf.save(output_file, **params)
            
            # Update progress
            self.compress_progress.setValue(pdf.page_count)
            QApplication.processEvents()
            
            # Show success message with file size comparison
            original_size = os.path.getsize(input_file) / (1024 * 1024)
            new_size = os.path.getsize(output_file) / (1024 * 1024)
            reduction = (1 - new_size / original_size) * 100
            
            QMessageBox.information(
                self, 
                "Success", 
                f"PDF compressed successfully!\n\n"
                f"Original size: {original_size:.2f} MB\n"
                f"New size: {new_size:.2f} MB\n"
                f"Reduction: {reduction:.2f}%"
            )
            
            # Update file info
            self.file_info.setText(
                f"Original file size: {original_size:.2f} MB\n"
                f"Compressed file size: {new_size:.2f} MB\n"
                f"Size reduction: {reduction:.2f}%"
            )
            
            # Close PDF
            pdf.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while compressing PDF file: {str(e)}")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFManager()
    window.show()
    sys.exit(app.exec())
