from PyQt5.QtWidgets import QTableView, QAction, QMenu, QMessageBox, qApp
from PyQt5.Qt import Qt, QHeaderView, QCursor
from SamAuthenticator.AddKeyDialog import AddKeyDialog
import SamAuthenticator.KeysDataModel as model


class KeyDataView(QTableView):
    def __init__(self):
        super().__init__()

        self.data_model = None

        self.add_key_dialog = AddKeyDialog()
        self.add_key_dialog.new_key_to_add_signal.connect(self.add_new_key)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuEvent)

    def contextMenuEvent(self, event):
        table_context_menu = QMenu(self)
        menu = QMenu(self)
        copy_action = QAction('Copy', self)
        copy_action.triggered.connect(self.copy_selected)
        add_key_action = QAction('Add new key', self)
        add_key_action.triggered.connect(self.add_new_key_from_dialog)
        remove_key_action = QAction('Remove key', self)
        remove_key_action.triggered.connect(self.remove_row)

        menu.addAction(copy_action)
        menu.addSeparator()
        menu.addAction(add_key_action)
        if len(self.selectedIndexes()) > 0:
            menu.addAction(remove_key_action)

        menu.popup(QCursor.pos())

    def copy_selected(self):
        cells = self.selectedIndexes()
        if len(cells) == 0:
            return
        if len(cells) != self.model().columnCount():
            return
        for el in cells:
            if el.column() == model.AuthenticatorKeysDataModel.TOKEN_COL:
                qApp.clipboard().setText(str(el.data()))

    def remove_row(self):
        cells = self.selectedIndexes()
        if len(cells) == 0:
            return
        if len(cells) != self.model().columnCount():
            return
        for el in cells:
            row = el.row()
            self.model().removeRow(row)
            return

    def add_new_key_from_dialog(self):
        self.add_key_dialog.get_new_key()

    def add_new_key(self, name, secret):
        try:
            self.data_model.getKeysObject().test_secret_validity(secret)
            self.data_model.getKeysObject().set_secret(name, secret)
            self.data_model.refreshAll()
        except Exception as e:
            self.add_key_dialog.close()
            QMessageBox.warning(self, "Error", "Testing the secret you entered failed. " + str(e))
            return

    def set_real_data_model(self, the_model):
        self.data_model = the_model
