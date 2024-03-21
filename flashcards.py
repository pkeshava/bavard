#%%

# flashcards_app.py
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtCore import Qt

class FlashcardApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        
    def initUI(self):
        # Layout and widgets
        self.layout = QVBoxLayout()
        self.current_idx = -1
        self.showing_english = True

        # Load data and initial settings
        #self.file_path = ''
        self.load_button = QPushButton('Load CSV')
        self.load_button.clicked.connect(self.load_csv)
        #self.df = pd.read_csv('data/translation_sorted.csv')
        #self.df = self.file_path
        
        self.flashcard_label = QLabel("Click 'Next' to start", self)
        self.flashcard_label.setAlignment(Qt.AlignCenter)
        self.flashcard_label.setWordWrap(True)
        
        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.next_card)
        
        self.reset_button = QPushButton("Start Over", self)
        self.reset_button.clicked.connect(self.start_over)

        # Add after the other buttons
        self.shuffle_button = QPushButton("Shuffle", self)
        self.shuffle_button.clicked.connect(self.shuffle_cards)
        
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.shuffle_button)
        self.layout.addWidget(self.flashcard_label)
        self.layout.addWidget(self.next_button)
        self.layout.addWidget(self.reset_button)
        
        self.setLayout(self.layout)
        
        
        # Set CSS styles
        style = """
            QWidget {
                background-color: #e6f7ff;
            }
            QLabel {
                font-size: 18px;
            }
            QPushButton {
                background-color: #d1e8ff;
                border: 1px solid #a5c6ff;
                padding: 5px 15px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c2daff;
            }
            QPushButton:pressed {
                background-color: #b3ccff;
            }
        """
        
        self.setStyleSheet(style)
    
    def load_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Select CSV File', '', 'CSV Files (*.csv)')
        if file_path:
            self.df = pd.read_csv(file_path)
            print("Flashcard set loaded!")
            print(self.df.head())
        else:
            print("choose a csv file with translations")
            exit

    def flip_card(self):
        if self.showing_english:
            self.flashcard_label.setText(self.df.at[self.current_idx, 'French'])
        else:
            self.flashcard_label.setText(self.df.at[self.current_idx, 'English'])
        self.showing_english = not self.showing_english
        
    def next_card(self):
        self.current_idx += 1
        if self.current_idx >= len(self.df):
            self.current_idx = 0
        self.showing_english = True
        self.flashcard_label.setText(self.df.at[self.current_idx, 'English'])
        self.flashcard_label.mousePressEvent = lambda event: self.flip_card()

    def start_over(self):
        self.current_idx = -1
        self.next_card()
    
    def shuffle_cards(self):
        self.df = self.df.sample(frac=1).reset_index(drop=True)
        self.current_idx = -1
        self.next_card()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FlashcardApp()
    ex.setWindowTitle('Flashcards')
    ex.setGeometry(300, 300, 400, 200)
    ex.show()
    sys.exit(app.exec_())

# %%


