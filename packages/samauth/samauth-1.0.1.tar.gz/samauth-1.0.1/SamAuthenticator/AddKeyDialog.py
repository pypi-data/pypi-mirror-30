from PyQt5.QtWidgets import QDialog, QMainWindow, QWidget, QTableView, QGridLayout, QLineEdit, QAction, qApp, QInputDialog, \
    QMessageBox, QPushButton
from PyQt5.QtCore import pyqtSignal


class AddKeyDialog(QDialog):
    new_key_to_add_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.main_layout = QGridLayout()

        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Name")
        self.key_field = QLineEdit()
        self.key_field.setPlaceholderText("Secret Key")
        self.ok_button = QPushButton("OK")

        self.main_layout.addWidget(self.name_field, 0, 0, 1, 1)
        self.main_layout.addWidget(self.key_field, 1, 0, 1, 1)
        self.main_layout.addWidget(self.ok_button, 2, 0, 1, 1)

        self.setLayout(self.main_layout)

        self.ok_button.clicked.connect(self.ok_clicked)

    def get_new_key(self):
        self.setModal(True)
        self.name_field.setFocus()
        self.name_field.setText("")
        self.key_field.setText("")
        self.open()

    def ok_clicked(self):
        self.new_key_to_add_signal.emit(self.name_field.text(), self.key_field.text())
        self.close()
