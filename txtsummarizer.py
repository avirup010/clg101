import sys
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                            QSlider, QSpinBox, QComboBox, QProgressBar, QFrame)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
import spacy
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from transformers import pipeline

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except:
    # If model isn't available, download it
    import os
    os.system('python -m spacy download en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

class SummarizationWorker(QThread):
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, text, method, ratio_or_count, is_ratio, language='english'):
        super().__init__()
        self.text = text
        self.method = method
        self.ratio_or_count = ratio_or_count
        self.is_ratio = is_ratio
        self.language = language
        
    def run(self):
        # Simulating longer processing for animation effect
        if len(self.text) < 1000:
            time.sleep(1)  # Add slight delay for short texts
            
        # Update progress (25%)
        self.progress.emit(25)
        
        if self.method == "Extractive - LSA":
            summary = self.sumy_summarize(self.text, LsaSummarizer)
        elif self.method == "Extractive - LexRank":
            summary = self.sumy_summarize(self.text, LexRankSummarizer)
        elif self.method == "Extractive - Luhn":
            summary = self.sumy_summarize(self.text, LuhnSummarizer)
        elif self.method == "Abstractive - Transformers":
            summary = self.transformers_summarize(self.text)
        else:  # Default to spaCy
            summary = self.spacy_summarize(self.text)
            
        # Update progress (100%)
        self.progress.emit(100)
        self.finished.emit(summary)
        
    def spacy_summarize(self, text):
        # Update progress
        self.progress.emit(40)
        
        # Process the text with spaCy
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents]
        
        # Calculate word frequency
        word_freq = {}
        for word in doc:
            if not word.is_stop and not word.is_punct and word.text.lower() not in word_freq:
                word_freq[word.text.lower()] = 1
            elif not word.is_stop and not word.is_punct:
                word_freq[word.text.lower()] += 1
        
        # Update progress
        self.progress.emit(60)
        
        # Calculate sentence scores
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            for word in nlp(sentence):
                if word.text.lower() in word_freq:
                    if i not in sentence_scores:
                        sentence_scores[i] = word_freq[word.text.lower()]
                    else:
                        sentence_scores[i] += word_freq[word.text.lower()]
        
        # Update progress
        self.progress.emit(80)
        
        if self.is_ratio:
            num_sentences = max(1, int(len(sentences) * self.ratio_or_count))
        else:
            num_sentences = min(self.ratio_or_count, len(sentences))
            
        # Get top N sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
        top_sentences = sorted(top_sentences, key=lambda x: x[0])  # Sort by original order
        
        summary = " ".join([sentences[i] for i, _ in top_sentences])
        return summary
    
    def sumy_summarize(self, text, summarizer_class):
        # Update progress
        self.progress.emit(40)
        
        parser = PlaintextParser.from_string(text, Tokenizer(self.language))
        stemmer = Stemmer(self.language)
        summarizer = summarizer_class(stemmer)
        summarizer.stop_words = get_stop_words(self.language)
        
        # Update progress
        self.progress.emit(70)
        
        if self.is_ratio:
            # Convert ratio to count for sumy
            num_sentences = max(1, int(len(sent_tokenize(text)) * self.ratio_or_count))
        else:
            num_sentences = self.ratio_or_count
            
        summary = " ".join(str(sentence) for sentence in summarizer(parser.document, num_sentences))
        return summary
    
    def transformers_summarize(self, text):
        # Update progress
        self.progress.emit(40)
        
        # Load summarization pipeline
        summarizer = pipeline("summarization")
        
        # Update progress
        self.progress.emit(60)
        
        # For longer texts, split into chunks
        max_chunk_length = 1024
        chunks = []
        
        current_length = 0
        current_chunk = ""
        
        for sentence in sent_tokenize(text):
            sentence_length = len(sentence)
            
            if current_length + sentence_length <= max_chunk_length:
                current_chunk += sentence + " "
                current_length += sentence_length
            else:
                chunks.append(current_chunk)
                current_chunk = sentence + " "
                current_length = sentence_length
                
        if current_chunk:
            chunks.append(current_chunk)
            
        # Update progress
        self.progress.emit(70)
        
        # Process each chunk
        summaries = []
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            
            # Calculate max_length based on ratio or absolute length
            if self.is_ratio:
                max_length = max(10, int(len(chunk.split()) * self.ratio_or_count))
            else:
                max_length = min(len(chunk.split()), self.ratio_or_count * 50)  # Approximation
                
            min_length = max(10, max_length // 2)
            
            # Ensure max_length is within limits
            max_length = min(max_length, 150)
            
            summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
            summaries.append(summary[0]['summary_text'])
            
            # Update progress proportionally
            progress = 70 + (i + 1) * 20 // len(chunks)
            self.progress.emit(progress)
            
        return " ".join(summaries)

class AnimatedFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("background-color: #f8f9fa; border-radius: 10px;")
        
        # Create animation for hover effect
        self.animation = QPropertyAnimation(self, b"styleSheet")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.styleSheet())
        self.animation.setEndValue("background-color: #e9ecef; border-radius: 10px;")
        self.animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.styleSheet())
        self.animation.setEndValue("background-color: #f8f9fa; border-radius: 10px;")
        self.animation.start()
        super().leaveEvent(event)

class TextSummarizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Elegant Text Summarizer')
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QLabel {
                font-size: 14px;
                color: #212529;
            }
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #ffffff;
                selection-background-color: #6c757d;
            }
            QPushButton {
                background-color: #4361ee;
                color: white;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a56d4;
            }
            QPushButton:pressed {
                background-color: #2c3e8c;
            }
            QComboBox, QSpinBox, QSlider {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
                background-color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #ced4da;
                border-radius: 5px;
                text-align: center;
                background-color: #e9ecef;
            }
            QProgressBar::chunk {
                background-color: #4361ee;
                border-radius: 5px;
            }
        """)
        
        # Main widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Elegant Text Summarizer")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4361ee; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Input frame
        input_frame = AnimatedFrame()
        input_layout = QVBoxLayout(input_frame)
        
        input_label = QLabel("Enter or paste your text here:")
        input_label.setStyleSheet("font-weight: bold;")
        input_layout.addWidget(input_label)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Paste your text here...")
        self.input_text.setMinimumHeight(200)
        input_layout.addWidget(self.input_text)
        
        main_layout.addWidget(input_frame)
        
        # Control frame
        control_frame = AnimatedFrame()
        control_layout = QHBoxLayout(control_frame)
        
        # Method selection
        method_layout = QVBoxLayout()
        method_label = QLabel("Summarization Method:")
        method_label.setStyleSheet("font-weight: bold;")
        method_layout.addWidget(method_label)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Extractive - spaCy", 
            "Extractive - LSA", 
            "Extractive - LexRank", 
            "Extractive - Luhn",
            "Abstractive - Transformers"
        ])
        method_layout.addWidget(self.method_combo)
        control_layout.addLayout(method_layout)
        
        # Length control - radio buttons replaced with combo
        length_layout = QVBoxLayout()
        length_label = QLabel("Length Control:")
        length_label.setStyleSheet("font-weight: bold;")
        length_layout.addWidget(length_label)
        
        self.length_mode = QComboBox()
        self.length_mode.addItems(["By Ratio", "By Sentence Count"])
        self.length_mode.currentIndexChanged.connect(self.toggleLengthControl)
        length_layout.addWidget(self.length_mode)
        
        # Stacked layout for controls
        self.ratio_layout = QVBoxLayout()
        ratio_label = QLabel("Summary Ratio:")
        self.ratio_layout.addWidget(ratio_label)
        
        self.ratio_slider = QSlider(Qt.Horizontal)
        self.ratio_slider.setRange(10, 80)
        self.ratio_slider.setValue(30)
        self.ratio_slider.setTickPosition(QSlider.TicksBelow)
        self.ratio_slider.setTickInterval(10)
        self.ratio_layout.addWidget(self.ratio_slider)
        
        self.ratio_value = QLabel(f"{self.ratio_slider.value() / 100:.2f}")
        self.ratio_value.setAlignment(Qt.AlignCenter)
        self.ratio_layout.addWidget(self.ratio_value)
        self.ratio_slider.valueChanged.connect(
            lambda v: self.ratio_value.setText(f"{v / 100:.2f}"))
        
        self.count_layout = QVBoxLayout()
        count_label = QLabel("Number of Sentences:")
        self.count_layout.addWidget(count_label)
        
        self.sentence_count = QSpinBox()
        self.sentence_count.setRange(1, 50)
        self.sentence_count.setValue(5)
        self.count_layout.addWidget(self.sentence_count)
        
        # Initially add ratio layout
        length_layout.addLayout(self.ratio_layout)
        length_layout.addLayout(self.count_layout)
        self.count_layout.setContentsMargins(0, 0, 0, 0)
        self.toggleLengthControl(0)  # Initially show ratio
        
        control_layout.addLayout(length_layout)
        
        # Summarize button
        button_layout = QVBoxLayout()
        button_layout.addStretch()
        
        self.summarize_btn = QPushButton("Summarize")
        self.summarize_btn.setMinimumHeight(50)
        self.summarize_btn.clicked.connect(self.summarizeText)
        button_layout.addWidget(self.summarize_btn)
        
        control_layout.addLayout(button_layout)
        
        main_layout.addWidget(control_frame)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(5)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Output frame
        output_frame = AnimatedFrame()
        output_layout = QVBoxLayout(output_frame)
        
        output_label = QLabel("Summary:")
        output_label.setStyleSheet("font-weight: bold;")
        output_layout.addWidget(output_label)
        
        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Your summary will appear here...")
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(200)
        output_layout.addWidget(self.output_text)
        
        # Stats
        self.stats_label = QLabel("")
        output_layout.addWidget(self.stats_label)
        
        main_layout.addWidget(output_frame)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Set up fade-in animation
        self.opacity_effect = QGraphicsOpacityEffect(central_widget)
        central_widget.setGraphicsEffect(self.opacity_effect)
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(500)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        QTimer.singleShot(100, self.fade_in_animation.start)
        
    def toggleLengthControl(self, index):
        if index == 0:  # Ratio
            for i in range(self.count_layout.count()):
                widget = self.count_layout.itemAt(i).widget()
                if widget:
                    widget.setVisible(False)
            for i in range(self.ratio_layout.count()):
                widget = self.ratio_layout.itemAt(i).widget()
                if widget:
                    widget.setVisible(True)
        else:  # Count
            for i in range(self.ratio_layout.count()):
                widget = self.ratio_layout.itemAt(i).widget()
                if widget:
                    widget.setVisible(False)
            for i in range(self.count_layout.count()):
                widget = self.count_layout.itemAt(i).widget()
                if widget:
                    widget.setVisible(True)
    
    def summarizeText(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            self.showMessage("Please enter some text to summarize.")
            return
        
        # Get parameters
        method = self.method_combo.currentText()
        is_ratio = self.length_mode.currentIndex() == 0
        
        if is_ratio:
            param = self.ratio_slider.value() / 100
        else:
            param = self.sentence_count.value()
        
        # Clear previous output
        self.output_text.clear()
        self.stats_label.clear()
        
        # Disable UI during processing
        self.setUIEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Create and start worker thread
        self.worker = SummarizationWorker(text, method, param, is_ratio)
        self.worker.progress.connect(self.updateProgress)
        self.worker.finished.connect(self.displaySummary)
        self.worker.start()
    
    def updateProgress(self, value):
        self.progress_bar.setValue(value)
    
    def displaySummary(self, summary):
        # Create fade-in animation for the summary
        self.output_text.setText(summary)
        
        # Calculate stats
        input_words = len(self.input_text.toPlainText().split())
        output_words = len(summary.split())
        reduction = (1 - (output_words / max(1, input_words))) * 100
        
        self.stats_label.setText(
            f"Original: {input_words} words | Summary: {output_words} words | "
            f"Reduction: {reduction:.1f}%"
        )
        
        # Re-enable UI
        self.setUIEnabled(True)
        
        # Hide progress bar with animation
        fade_out = QPropertyAnimation(self.progress_bar, b"maximumHeight")
        fade_out.setDuration(300)
        fade_out.setStartValue(5)
        fade_out.setEndValue(0)
        fade_out.start()
        QTimer.singleShot(300, lambda: self.progress_bar.setVisible(False))
    
    def setUIEnabled(self, enabled):
        self.input_text.setEnabled(enabled)
        self.method_combo.setEnabled(enabled)
        self.length_mode.setEnabled(enabled)
        self.ratio_slider.setEnabled(enabled)
        self.sentence_count.setEnabled(enabled)
        self.summarize_btn.setEnabled(enabled)
        
        if not enabled:
            self.summarize_btn.setText("Processing...")
        else:
            self.summarize_btn.setText("Summarize")
    
    def showMessage(self, message):
        self.stats_label.setText(message)
        QTimer.singleShot(3000, self.stats_label.clear)

if __name__ == "__main__":
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistent cross-platform look
    
    window = TextSummarizer()
    window.show()
    sys.exit(app.exec_())