
#%% Flashcard app v2
# https://chat.openai.com/share/5710da7c-219d-43f4-97b5-73a8905f4aed


#%%

import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QWidget, QFormLayout, QMessageBox
import random

# class CustomLineEdit(QLineEdit):
#     def keyPressEvent(self, event):
#         if event.isAutoRepeat():  # Ignore auto-repeated key presses
#             return
#         super().keyPressEvent(event)

from PyQt5.QtCore import QTimer

class CustomLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(CustomLineEdit, self).__init__(*args, **kwargs)
        self.ignore_next = False

    def keyPressEvent(self, event):
        if self.ignore_next:
            self.ignore_next = False
            return

        if event.isAutoRepeat():  # Detecting auto-repeated key presses
            current_text = self.text()
            if len(current_text) > 0:
                self.setText(current_text[:-1])  # Remove the last character
            self.ignore_next = True
            return

        super().keyPressEvent(event)


class FlashcardApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Flashcard GUI")
        self.setGeometry(100, 100, 400, 200)

        # Layouts and Widgets
        layout = QVBoxLayout()

        self.select_csv_btn = QPushButton("Select CSV")
        self.select_csv_btn.clicked.connect(self.load_csv)
        layout.addWidget(self.select_csv_btn)

        self.word_label = QLabel("English Word")
        layout.addWidget(self.word_label)

        form_layout = QFormLayout()
        #self.translation_input = QLineEdit(self)
        self.translation_input = CustomLineEdit(self)
        form_layout.addRow("Translation: ", self.translation_input)
        self.check_btn = QPushButton("Enter")
        self.check_btn.clicked.connect(self.check_translation)
        form_layout.addRow(self.check_btn)
        layout.addLayout(form_layout)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_word)
        layout.addWidget(self.next_btn)

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close_app)
        layout.addWidget(self.exit_btn)

        self.randomize_btn = QPushButton("Randomize")
        self.randomize_btn.clicked.connect(self.randomize_words)
        layout.addWidget(self.randomize_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Data attributes
        self.words_df = None
        self.current_idx = -1

        # enter key enters
        self.translation_input.returnPressed.connect(self.check_translation)

        # load default file already translated
        self.default_list_btn = QPushButton("Default List")
        self.default_list_btn.clicked.connect(self.load_default_list)
        layout.addWidget(self.default_list_btn)

        self.answer_checked = False

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
        fname = QFileDialog.getOpenFileName(self, "Open CSV file", "", "CSV Files (*.csv);;All Files (*)")[0]
        if fname:
            try:
                self.words_df = pd.read_csv(fname, header=None)
                if self.words_df.shape[1] != 2:
                    raise ValueError("The CSV file must have exactly two columns.")
                self.current_idx = 0
                self.display_word()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
    
    def load_default_list(self):
        default_file = "data/translated_without_theme.csv"
        try:
            self.words_df = pd.read_csv(default_file, header=None)
            if self.words_df.shape[1] != 2:
                raise ValueError("The CSV file must have exactly two columns.")
            self.current_idx = 0
            self.display_word()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def display_word(self):
        if self.words_df is not None and 0 <= self.current_idx < len(self.words_df):
            self.word_label.setText(self.words_df.iloc[self.current_idx, 1])
            self.translation_input.clear()
            self.result_label.clear()

    # def check_translation(self):
    #     if self.words_df is not None and 0 <= self.current_idx < len(self.words_df):
    #         correct_translation = self.words_df.iloc[self.current_idx, 0].strip().lower()
    #         user_translation = self.translation_input.text().strip().lower()
    #         if user_translation == correct_translation:
    #             self.result_label.setText("Correct!")
    #         else:
    #             self.result_label.setText(f"Incorrect! Correct answer: {correct_translation}")
    def check_translation(self):
        if self.answer_checked:  # If already checked, load the next word
            self.next_word()
            return

        if self.words_df is not None and 0 <= self.current_idx < len(self.words_df):
            correct_translation = self.words_df.iloc[self.current_idx, 0].strip().lower()  # 1 is the index for English translation
            user_translation = self.translation_input.text().strip().lower()
            if user_translation == correct_translation:
                self.result_label.setText("Correct!")
            else:
                self.result_label.setText(f"Incorrect! Correct answer: {correct_translation}")
            
            self.answer_checked = True


    def next_word(self):
        self.answer_checked = False
        if self.words_df is not None:
            self.current_idx += 1
            if self.current_idx >= len(self.words_df):
                self.current_idx = 0
            self.display_word()

    def randomize_words(self):
        if self.words_df is not None:
            self.words_df = self.words_df.sample(frac=1).reset_index(drop=True)
            self.current_idx = 0
            self.display_word()

    def close_app(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlashcardApp()
    window.show()
    sys.exit(app.exec_())


# %%
