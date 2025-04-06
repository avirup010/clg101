import tkinter as tk
import pygame
import numpy as np

# Initialize Pygame mixer for sound (stereo, 2 channels)
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Frequencies for Sargam notes (based on Sa at 261.63 Hz, approximating a common scale)
NOTE_FREQUENCIES = {
    'Sa': 261.63,  # Sa (tonic, equivalent to C4)
    'Re': 294.33,  # Re (approximated as D4)
    'Ga': 327.03,  # Ga (approximated as E4)
    'Ma': 348.83,  # Ma (approximated as F4)
    'Pa': 392.44,  # Pa (approximated as G4)
    'Dha': 436.05, # Dha (approximated as A4)
    'Ni': 490.55,  # Ni (approximated as B4)
    'Sa2': 523.25  # Higher Sa (octave up, equivalent to C5)
}

# Generate a simple sine wave sound for a given frequency
def generate_tone(frequency, duration=0.5, volume=0.5):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    tone = np.sin(frequency * t * 2 * np.pi)
    sound = (tone * volume * 32767).astype(np.int16)  # 1D array (mono)
    # Convert to 2D array for stereo: duplicate the mono signal for both channels
    stereo_sound = np.column_stack((sound, sound))
    return pygame.sndarray.make_sound(stereo_sound)

# Pre-generate sounds for each note
sounds = {note: generate_tone(NOTE_FREQUENCIES[note]) for note in NOTE_FREQUENCIES}

# Main application class
class PianoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sargam Piano")
        self.root.geometry("800x200")  # Wider window for 8 keys
        self.root.configure(bg="#2b2b2b")  # Dark background for minimal look

        # Frame for piano keys
        self.key_frame = tk.Frame(self.root, bg="#2b2b2b")
        self.key_frame.pack(expand=True, pady=20)

        # Create piano keys
        self.keys = {}
        self.create_keys()

        # Bind window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_keys(self):
        key_width = 80
        key_height = 150
        notes = ['Sa', 'Re', 'Ga', 'Ma', 'Pa', 'Dha', 'Ni', 'Sa2']  # Sargam notes

        for i, note in enumerate(notes):
            key = tk.Canvas(self.key_frame, width=key_width, height=key_height, bg="white", highlightthickness=2, highlightbackground="#1a1a1a")
            key.grid(row=0, column=i, padx=2)
            key.create_text(key_width//2, key_height//2, text=note, font=("Arial", 20, "bold"), fill="black")
            key.bind("<Button-1>", lambda event, n=note: self.play_note(n))
            key.bind("<ButtonRelease-1>", lambda event, n=note: self.release_note(n))
            self.keys[note] = key

    def play_note(self, note):
        # Animation: Change color and slightly shrink key
        self.keys[note].configure(bg="#d3d3d3")
        self.keys[note].config(width=76, height=145)
        
        # Play sound
        sounds[note].play()

    def release_note(self, note):
        # Animation: Restore original size and color
        self.keys[note].configure(bg="white")
        self.keys[note].config(width=80, height=150)

    def on_closing(self):
        pygame.mixer.quit()
        self.root.destroy()

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = PianoApp(root)
    root.mainloop()