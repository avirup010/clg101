# Section 1: Main Application and UI
import sys
import os
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QLabel, QFileDialog, QTextEdit, QWidget, QProgressBar, QFrame)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QThread
from PyQt5.QtGui import QColor, QPalette, QFont, QIcon

# Import our audio processing and summarization modules
from audio_processing import AudioProcessor
from summarization import Summarizer

class WorkerThread(QThread):
    update_progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    
    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file
        
    def run(self):
        # Process audio file
        audio_processor = AudioProcessor()
        self.update_progress.emit(25)
        
        transcript = audio_processor.transcribe(self.audio_file)
        self.update_progress.emit(50)
        
        # Generate summary
        summarizer = Summarizer()
        summary = summarizer.generate_summary(transcript)
        self.update_progress.emit(100)
        
        # Emit the summary as the result
        self.finished.emit(summary)

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4A55A2;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #7895CB;
            }
            QPushButton:pressed {
                background-color: #A0BFE0;
            }
        """)
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.setDuration(150)
        
    def enterEvent(self, event):
        rect = self.geometry()
        self._animation.setStartValue(rect)
        self._animation.setEndValue(QRect(rect.x(), rect.y() - 3, rect.width(), rect.height()))
        self._animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        rect = self.geometry()
        self._animation.setStartValue(rect)
        self._animation.setEndValue(QRect(rect.x(), rect.y() + 3, rect.width(), rect.height()))
        self._animation.start()
        super().leaveEvent(event)

class MeetingSummarizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("AI Meeting Summarizer")
        self.setMinimumSize(1280, 720)  # HD resolution
        self.setStyleSheet("background-color: #F5F5F5;")
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Title section
        title_label = QLabel("AI Meeting Summarizer")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #4A55A2; margin: 20px;")
        main_layout.addWidget(title_label)
        
        # File selection section
        file_section = QHBoxLayout()
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("padding: 10px; background-color: white; border-radius: 5px;")
        self.file_path_label.setFont(QFont("Arial", 12))
        self.browse_button = AnimatedButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        file_section.addWidget(self.file_path_label, 7)
        file_section.addWidget(self.browse_button, 3)
        main_layout.addLayout(file_section)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                margin: 20px 0;
            }
            QProgressBar::chunk {
                background-color: #7895CB;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # Summary section
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.StyledPanel)
        summary_frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 10px;")
        summary_layout = QVBoxLayout(summary_frame)
        
        summary_header = QLabel("Meeting Summary")
        summary_header.setFont(QFont("Arial", 16, QFont.Bold))
        summary_header.setStyleSheet("color: #4A55A2;")
        summary_layout.addWidget(summary_header)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(QFont("Arial", 12))
        self.summary_text.setStyleSheet("border: none;")
        summary_layout.addWidget(self.summary_text)
        
        main_layout.addWidget(summary_frame)
        
        # Process button
        self.process_button = AnimatedButton("Generate Summary")
        self.process_button.clicked.connect(self.process_audio)
        self.process_button.setEnabled(False)
        main_layout.addWidget(self.process_button)
        
        # Status bar for messages
        self.statusBar().showMessage("Ready")
        
        # Apply animations to the summary frame
        self.summary_animation = QPropertyAnimation(summary_frame, b"geometry")
        self.summary_animation.setEasingCurve(QEasingCurve.OutBack)
        self.summary_animation.setDuration(500)
        
        # Show the window
        self.show()
        
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.m4a *.ogg)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            self.process_button.setEnabled(True)
            self.statusBar().showMessage(f"File selected: {os.path.basename(file_path)}")
            
            # Animate the file selection
            self.file_path_label.setStyleSheet("padding: 10px; background-color: #E8F0FE; border-radius: 5px;")
            animation = QPropertyAnimation(self.file_path_label, b"styleSheet")
            animation.setDuration(500)
            animation.setStartValue("padding: 10px; background-color: #E8F0FE; border-radius: 5px;")
            animation.setEndValue("padding: 10px; background-color: white; border-radius: 5px;")
            animation.start()
            
    def process_audio(self):
        if not self.file_path_label.text() or self.file_path_label.text() == "No file selected":
            self.statusBar().showMessage("Please select an audio file first")
            return
            
        # Disable the process button during processing
        self.process_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.statusBar().showMessage("Processing audio file...")
        
        # Reset progress
        self.progress_bar.setValue(0)
        
        # Create and start worker thread
        self.worker = WorkerThread(self.file_path_label.text())
        self.worker.update_progress.connect(self.update_progress)
        self.worker.finished.connect(self.update_summary)
        self.worker.start()
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def update_summary(self, summary):
        # Re-enable buttons
        self.process_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        
        # Update the summary text with an animation
        current_geometry = self.summary_text.parent().geometry()
        self.summary_animation.setStartValue(current_geometry)
        self.summary_animation.setEndValue(current_geometry)
        self.summary_animation.start()
        
        # Set the text with a typing effect
        self.summary_text.clear()
        self.type_text(summary)
        
        self.statusBar().showMessage("Summary generated successfully")
        
    def type_text(self, text, speed=30):
        """Simulate typing effect for the summary text"""
        self.full_text = text
        self.text_position = 0
        
        def add_character():
            if self.text_position < len(self.full_text):
                self.summary_text.insertPlainText(self.full_text[self.text_position])
                self.text_position += 1
                threading.Timer(1.0/speed, add_character).start()
        
        add_character()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a modern look
    window = MeetingSummarizerApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

# Section 2: Audio Processing
class AudioProcessor:
    def __init__(self):
        """Initialize the audio processor with speech recognition capabilities"""
        # Import here to avoid loading these libraries until needed
        import speech_recognition as sr
        import librosa
        import numpy as np
        
        self.recognizer = sr.Recognizer()
        
    def transcribe(self, audio_file):
        """
        Transcribe an audio file to text using speech recognition
        
        Args:
            audio_file (str): Path to the audio file
            
        Returns:
            str: Transcribed text
        """
        import speech_recognition as sr
        
        # For very large files, we might want to split them
        # This is a simplified version
        try:
            # Load audio file
            with sr.AudioFile(audio_file) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source)
                
                # Record the audio
                audio_data = self.recognizer.record(source)
                
                # Use Google's speech recognition
                # In a production app, you might want to use a paid API for better results
                text = self.recognizer.recognize_google(audio_data)
                
                return text
        except Exception as e:
            # In a real app, you'd handle different exceptions separately
            return f"Error transcribing audio: {str(e)}"
    
    def transcribe_large_file(self, audio_file):
        """
        Handle large audio files by splitting them into chunks
        
        Args:
            audio_file (str): Path to the audio file
            
        Returns:
            str: Transcribed text
        """
        import speech_recognition as sr
        import librosa
        import numpy as np
        from pydub import AudioSegment
        import tempfile
        
        # For demonstration purposes, this is a simplified implementation
        try:
            # Convert to wav if needed
            sound = AudioSegment.from_file(audio_file)
            
            # Split audio into 30-second chunks
            chunk_length_ms = 30000  # 30 seconds
            chunks = [sound[i:i+chunk_length_ms] for i in range(0, len(sound), chunk_length_ms)]
            
            transcript = ""
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                # Export chunk to a temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
                    chunk.export(temp_file.name, format="wav")
                    
                    with sr.AudioFile(temp_file.name) as source:
                        audio_data = self.recognizer.record(source)
                        try:
                            text = self.recognizer.recognize_google(audio_data)
                            transcript += text + " "
                        except:
                            transcript += "[inaudible] "
            
            return transcript
        except Exception as e:
            return f"Error processing large audio file: {str(e)}"

# Section 3: Summarization
class Summarizer:
    def __init__(self):
        """Initialize the summarizer with NLP models"""
        # Import here to avoid loading these libraries until needed
        try:
            from transformers import pipeline
            # You would need to install transformers and torch
            # The first time this runs it will download the model
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        except ImportError:
            # Fallback to a simpler summarizer if transformers is not available
            self.summarizer = None
    
    def generate_summary(self, text):
        """
        Generate a summary from the transcribed text
        
        Args:
            text (str): The transcribed text to summarize
            
        Returns:
            str: Summarized text
        """
        if not text:
            return "No transcript was provided to summarize."
        
        # If we have the transformers library and model
        if self.summarizer:
            try:
                # For long texts, we need to chunk it
                # BART has a max input length
                if len(text) > 1024:
                    chunks = self._split_into_chunks(text, 1024)
                    summaries = []
                    
                    for chunk in chunks:
                        summary = self.summarizer(chunk, max_length=150, min_length=30, do_sample=False)
                        summaries.append(summary[0]['summary_text'])
                    
                    # Combine chunk summaries and summarize again for coherence
                    final_text = " ".join(summaries)
                    if len(final_text) > 1024:
                        final_summary = self.summarizer(final_text[:1024], max_length=150, min_length=30, do_sample=False)
                        return final_summary[0]['summary_text']
                    else:
                        return final_text
                else:
                    summary = self.summarizer(text, max_length=150, min_length=30, do_sample=False)
                    return summary[0]['summary_text']
            except Exception as e:
                # Fallback to the simple summarizer
                return self._simple_summarize(text) + f"\n\nNote: Advanced summarization failed with error: {str(e)}"
        else:
            # Use a simple extractive summarization method
            return self._simple_summarize(text)
    
    def _simple_summarize(self, text, sentences=5):
        """A simple extractive summarization method"""
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import sent_tokenize, word_tokenize
        from nltk.probability import FreqDist
        
        try:
            # Download necessary NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            # Tokenize the text into sentences and words
            sentences = sent_tokenize(text)
            words = word_tokenize(text.lower())
            
            # Remove stopwords
            stop_words = set(stopwords.words('english'))
            words = [word for word in words if word not in stop_words and word.isalnum()]
            
            # Calculate word frequencies
            freq = FreqDist(words)
            
            # Score sentences based on word frequencies
            sentence_scores = {}
            for i, sentence in enumerate(sentences):
                for word in word_tokenize(sentence.lower()):
                    if word in freq:
                        if i in sentence_scores:
                            sentence_scores[i] += freq[word]
                        else:
                            sentence_scores[i] = freq[word]
            
            # Get top sentences
            import heapq
            summary_sentences = heapq.nlargest(min(5, len(sentences)), 
                                              sentence_scores.items(), 
                                              key=lambda x: x[1])
            
            # Sort by original position to maintain flow
            summary_sentences.sort()
            
            # Combine the top sentences
            summary = ' '.join([sentences[i] for i, _ in summary_sentences])
            return summary
        except Exception as e:
            # Very basic fallback
            if len(text) > 1000:
                return text[:1000] + "... (Summary failed: " + str(e) + ")"
            else:
                return text
    
    def _split_into_chunks(self, text, chunk_size):
        """Split text into chunks of approximately equal size"""
        sentences = sent_tokenize(text)
        current_chunk = []
        chunks = []
        current_size = 0
        
        for sentence in sentences:
            current_size += len(sentence)
            if current_size > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_size = len(sentence)
            else:
                current_chunk.append(sentence)
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks