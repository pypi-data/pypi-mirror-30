from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QLineEdit, QAction, qApp, QInputDialog, \
    QMessageBox, QFileDialog
from PyQt5.QtCore import QSortFilterProxyModel, pyqtSlot, QSettings
from PyQt5.Qt import Qt, QIcon, QSizePolicy
import SamAuthenticator.KeysDataModel as model
import SamAuthenticator.KeyDataView as dataview
import SamAuthenticator.Authenticator as auth
import SamAuthenticator.TrayIcon as tray
import functools
import os


class AuthenticatorGUI(QMainWindow):
    new_key_to_add_slot = pyqtSlot(str, str)

    def __init__(self):
        super().__init__()
        self.data_file_name = "data.dat"

        self.load_geometry()

        current_path = os.path.dirname(os.path.abspath(__file__))
        main_icon = QIcon(os.path.join(current_path, "images/key.png"))
        # self.setWindowIcon(main_icon)

        self.tray_icon = tray.SamAuthenticatorTrayIcon(self, main_icon)
        self.tray_icon.show()

        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)

        self.main_layout = QGridLayout()
        self.filter_line_edit = QLineEdit()
        self.filter_line_edit.setPlaceholderText("Enter filter (Ctrl+F)")
        self.keys_table_view = dataview.KeyDataView()

        self.keys_data_model = None
        self.keys_data_model_proxy = None
        self.setup_data_model(auth.AuthenticatorKeys())

        self.main_layout.addWidget(self.filter_line_edit, 1, 0, 1, 2)
        self.main_layout.addWidget(self.keys_table_view, 2, 0, 1, 2)

        self.mainWidget.setLayout(self.main_layout)

        self.filter_line_edit.textChanged.connect(self.set_filter_string)

        self.add_menus()
        self.add_toolbar()

        self.setWindowTitle('Sam Authenticator')
        self.show()
        self.load_data_from_default_path()

    def set_filter_string(self, filter_str):
        if self.keys_data_model_proxy is not None:
            self.keys_data_model_proxy.setFilterWildcard(filter_str)

    def set_data_file_name(self, file_name):
        self.data_file_name = file_name

    def import_data(self):
        file_name = QFileDialog.getOpenFileName(self, "Import data from...", "", "Encrypted data (*.dat, *.*)")
        # if a file is chosen
        if file_name[1]:
            if os.path.exists(file_name[0]):
                self.load_data_from(file_name[0])
            else:
                QMessageBox.warning(self, "File not found", "The path you chose doesn't contain a file.")

    def load_data_from_default_path(self):
        if not os.path.exists(self.data_file_name):
            return

        self.load_data_from(self.data_file_name)
        self.filter_line_edit.clear()

    def decrypt_data_file(self):
        source_file = QFileDialog.getOpenFileName(self, "Choose the file to decrypt...", "", "Encrypted data (*.dat, *.*)")
        # if a file is chosen
        if not source_file[1]:
            return

        if not os.path.exists(source_file[0]):
            QMessageBox.warning(self, "File not found", "The path you chose doesn't contain a file.")
            return

        dest_file = QFileDialog.getSaveFileName(self, "Save decrypted file as...", "", "JSON file (.json)")
        # if a file is chosen
        if not dest_file[1]:
            return

        password_from_dialog = QInputDialog.getText(self, "Input encryption password",
                                                          "Encryption password:",
                                                          QLineEdit.Password, "")
        ok_pressed = password_from_dialog[1]
        if not ok_pressed:
            return

        try:
            with open(source_file[0], 'rb') as f_load:
                ciphered_data = f_load.read()
                readable_data = auth.decrypt_data(ciphered_data, password_from_dialog[0], auth.get_default_salt())

                with open(dest_file[0], 'wb') as f_save:
                    f_save.write(readable_data)

        except Exception as e:
            QMessageBox.warning(self, "Error", "Decryption failed. " + str(e))

    def load_data_from(self, data_file_path):
        password_from_dialog = QInputDialog.getText(self, "Input encryption password",
                                                "Encryption password:",
                                                QLineEdit.Password, "")
        ok_pressed = password_from_dialog[1]
        if not ok_pressed:
            return

        try:
            keys = auth.read_keys_from_file(password_from_dialog[0], data_file_path)
            self.setup_data_model(keys)
        except Exception as e:
            QMessageBox.warning(self, "Unable to read data", "Unable to read data. " + str(e))

    def save_data(self, data_file):
        pass_from_dialog = QInputDialog.getText(self, "Input encryption password",
                                                "New encryption password:",
                                                QLineEdit.Password, "")
        ok_pressed = pass_from_dialog[1]
        if not ok_pressed:
            return

        password = pass_from_dialog[0]

        if self.keys_data_model is not None:
            auth.write_keys_to_file(self.keys_data_model.getKeysObject(), password, data_file)
        else:
            QMessageBox.warning(self, "No data loaded", "Data should be loaded before attempting to save it")

    def save_data_as(self):
        file_name = QFileDialog.getSaveFileName(self, "Save data as...", "", "Encrypted data (*.dat)")
        # if a file is chosen
        if file_name[1]:
            self.save_data(file_name[0])

    def add_menus(self):
        exit_act = QAction('&Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('Exit application')
        exit_act.triggered.connect(qApp.quit)

        reload_data_act = QAction('&Reload data from default location (' + self.data_file_name + ')' , self)
        reload_data_act.setStatusTip('Reload data from file')
        reload_data_act.setShortcut('Ctrl+R')
        reload_data_act.triggered.connect(self.load_data_from_default_path)

        save_data_act = QAction('&Save data to default location (' + self.data_file_name + ')', self)
        save_data_act.setShortcut('Ctrl+S')
        save_data_act.setStatusTip('Save data to the default path')
        save_data_act.triggered.connect(functools.partial(self.save_data, self.data_file_name))

        save_data_as_act = QAction('&Save data as...', self)
        save_data_as_act.setShortcut('Ctrl+Shift+S')
        save_data_as_act.setStatusTip('Save data to...')
        save_data_as_act.triggered.connect(self.save_data_as)

        import_data_act = QAction('&Import data from...' , self)
        import_data_act.setStatusTip('Import data from a file...')
        import_data_act.triggered.connect(self.import_data)

        decrypt_data_file_act = QAction('&Decrypt a data file', self)
        decrypt_data_file_act.setStatusTip('Decrypt a data file to raw text (unsafe)')
        decrypt_data_file_act.triggered.connect(self.decrypt_data_file)

        QAction("File")
        file_menu = self.menuBar().addMenu('&File')
        file_menu.addAction(reload_data_act)
        file_menu.addAction(save_data_act)
        file_menu.addSeparator()
        file_menu.addAction(import_data_act)
        file_menu.addAction(save_data_as_act)
        file_menu.addSeparator()
        file_menu.addAction(decrypt_data_file_act)
        file_menu.addSeparator()
        file_menu.addAction(exit_act)

    def add_toolbar(self):
        toolbar = self.addToolBar("File")

        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        current_path = os.path.dirname(os.path.abspath(__file__))
        toolbar.addWidget(left_spacer)
        add_act = QAction(QIcon(os.path.join(current_path, "images/add.png")), "Add new key", self)
        add_act.setShortcut('Ctrl+A')
        toolbar.addAction(add_act)
        remove_act = QAction(QIcon(os.path.join(current_path, "images/delete.png")), "Remove selected key", self)
        remove_act.setShortcut('Ctrl+D')
        toolbar.addAction(remove_act)
        toolbar.addWidget(right_spacer)

        add_act.triggered.connect(self.keys_table_view.add_new_key_from_dialog)
        remove_act.triggered.connect(self.keys_table_view.remove_row)

    def setup_data_model(self, keys):
        self.keys_data_model_proxy = QSortFilterProxyModel()
        self.keys_data_model_proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.keys_data_model = model.AuthenticatorKeysDataModel(keys)
        self.keys_table_view.set_real_data_model(self.keys_data_model)
        self.keys_data_model_proxy.setSourceModel(self.keys_data_model)
        self.keys_table_view.setModel(self.keys_data_model_proxy)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            self.keys_table_view.copy_selected()
        if event.key() == Qt.Key_F and event.modifiers() & Qt.ControlModifier:
            self.filter_line_edit.setFocus()
            self.filter_line_edit.selectAll()
        if event.key() == Qt.Key_Escape:
            self.filter_line_edit.clear()

    def load_geometry(self):
        settings = QSettings("SamApps", "SamAuthenticator")
        geometry_values = settings.value("geometry")
        if geometry_values is not None:
            self.restoreGeometry(geometry_values)

    def closeEvent(self, event):
        settings = QSettings("SamApps", "SamAuthenticator")
        settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)
