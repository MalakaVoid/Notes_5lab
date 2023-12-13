from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QTabWidget, \
    QFormLayout, QCheckBox, QComboBox
from PyQt5.QtGui import QFont, QColor

from cassandra_controller import *


class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.username_label = QLabel('Username')
        self.username_input = QLineEdit()
        self.password_label = QLabel('Password')
        self.password_input = QLineEdit()
        self.login_button = QPushButton('Login')
        self.register_button = QPushButton('Register')

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.login_button.clicked.connect(self.check_credentials)
        self.register_button.clicked.connect(self.register)

        self.setLayout(layout)

    def check_credentials(self):
        result = login_user(self.username_input.text(), self.password_input.text())
        if result == 404:
            self.username_label.setText('Username (User does not exist)')
            return
        if result == 500:
            self.password_label.setText('Password (Incorrect password)')
            return

        self.notes_widget = Notes(result)
        self.notes_widget.show()
        self.close()

    def register(self):
        result = register_user(self.username_input.text(), self.password_input.text())
        if result == 500:
            self.username_label.setText('Username (User already exists)')
            return
        if result == 404:
            self.username_label.setText('Something went wrong')
            return
        self.username_label.setText('Username (Registration successful, you can now login)')


class Notes(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.initUI()
        self.counter = 0

    def initUI(self):
        layout = QVBoxLayout()
        self.setMinimumSize(QSize(600, 600))

        self.notes_tab = QTabWidget()
        self.add_button = QPushButton('Add Note')
        self.save_button = QPushButton('Save')
        self.delete_button = QPushButton('Delete')
        self.presets_button = QPushButton('Create Preset')
        self.metadata_button = QPushButton('Metadata')

        layout.addWidget(self.notes_tab)
        layout.addWidget(self.add_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.presets_button)
        layout.addWidget(self.metadata_button)

        self.add_button.clicked.connect(lambda: self.add_new_note(f'Note {self.notes_tab.count()}'))
        self.save_button.clicked.connect(self.save_notes)
        self.delete_button.clicked.connect(self.delete_notes)
        self.presets_button.clicked.connect(self.open_presets_page)
        self.metadata_button.clicked.connect(self.open_metadata_page)

        self.setLayout(layout)
        
        self.load_notes()

    def load_notes(self):
        notes = get_user_notes(self.user_id)
        for note in notes:
            if note is not None:
                title = f"Note {self.notes_tab.count()}"
                edit_note_title(title, note.note_id)
                self.add_note(title, note.text, note.note_id)

    def add_new_note(self, title, text=''):
        result = add_note(title, text, self.user_id)
        if result == 404:
            return
        self.add_note(title, text)

    def add_note(self, title, text='', note_id=None):
        note_widget = QTextEdit()
        note_widget.setText(text)

        style_dict = None
        if note_id is not None:
            style_dict = get_preset(note_id, self.user_id)

        if style_dict is not None:
            q_font = QFont(style_dict.font, int(style_dict.font_size))
            q_font.setItalic(style_dict.is_italic)
            q_font.setBold(style_dict.is_bold)

            note_widget.setFont(q_font)

            note_text_color = QColor(style_dict.color).name()
            note_widget.setStyleSheet("QTextEdit {color: $note_text_color;}".replace('$note_text_color', note_text_color))

        self.notes_tab.addTab(note_widget, title)

    def open_presets_page(self):
        self.save_notes()
        self.preset_pages = list()
        self.preset_pages.append(Presets(f"Note {self.notes_tab.currentIndex()}", self.user_id, self))

        self.preset_pages[0].show()

    def save_notes(self):
        note_widget = self.notes_tab.widget(self.notes_tab.currentIndex())
        title = f"Note {self.notes_tab.currentIndex()}"
        text = note_widget.toPlainText()
        edit_note(title, text, self.user_id)

    def update_window(self):
        self.notes_tab.clear()
        self.load_notes()

    def open_metadata_page(self):
        note_id = get_note_id_by_title(self.user_id, f"Note {self.notes_tab.currentIndex()}")
        self.metadata_page = Metadata(note_id)
        self.metadata_page.show()

    def delete_notes(self):
        note_id = get_note_id_by_title(self.user_id, f"Note {self.notes_tab.currentIndex()}")
        delete_note(note_id)
        self.update_window()


class Presets(QWidget):
    def __init__(self, note_id, user_id, notes_window):
        super().__init__()
        self.notes_window = notes_window
        self.note_id = get_note_id_by_title(user_id, note_id)
        self.user_id = user_id
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('My Form')

        mainLayout = QVBoxLayout()
        formLayout = QFormLayout()

        # Int field
        self.intField = QLineEdit()
        formLayout.addRow('Font size:', self.intField)

        # Bool fields
        self.boolField1 = QCheckBox()
        formLayout.addRow('Italic:', self.boolField1)

        self.boolField2 = QCheckBox()
        formLayout.addRow('Bold:', self.boolField2)

        # Enum field
        self.enumField = QComboBox()
        self.enumField.addItems(["black", "red", "green", "blue", "pink", "orange", "yellow"])
        formLayout.addRow('Color:', self.enumField)

        # Enum field 2
        self.enumField2 = QComboBox()
        self.enumField2.addItems(["Times New Roman", "Arial", "Consolas"])
        formLayout.addRow('Color:', self.enumField2)

        # button
        self.save_button = QPushButton('Save')

        self.save_button.clicked.connect(self.save)

        mainLayout.addLayout(formLayout)
        mainLayout.addWidget(self.save_button)
        self.setLayout(mainLayout)

        temp = get_preset(self.note_id, self.user_id)
        if temp is not None:
            self.intField.setText(str(temp.font_size))
            self.boolField1.setCheckState(temp.is_italic)
            self.boolField2.setCheckState(temp.is_bold)
            self.enumField.setCurrentText(temp.color)
            self.enumField2.setCurrentText(temp.font)

    def save(self):
        if len(self.intField.text()) < 1: return

        create_preset(self.note_id, self.intField.text(), self.boolField1.isChecked(),self.boolField2.isChecked(),
                      self.enumField.currentText(), self.enumField2.currentText())

        self.notes_window.update_window()
        self.close()


class Metadata(QWidget):
    def __init__(self, note_id):
        super().__init__()
        self.note_id = note_id
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        metadata = get_note_metadata(self.note_id)

        self.creation_date_label = QLabel(f'Creation date: {metadata.creation_date}')
        self.updation_date_label = QLabel(f'Update date: {metadata.creation_date}')

        layout.addWidget(self.creation_date_label)
        layout.addWidget(self.updation_date_label)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication([])
    login = Login()
    login.show()
    app.exec_()
