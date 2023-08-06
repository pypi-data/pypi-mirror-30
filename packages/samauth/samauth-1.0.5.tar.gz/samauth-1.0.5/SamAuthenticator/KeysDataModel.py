from PyQt5 import QtCore
from PyQt5.Qt import Qt, pyqtSignal
import SamAuthenticator.Authenticator as auth


class AuthenticatorKeysDataModel(QtCore.QAbstractTableModel):
    tokensUpdatedSignal = pyqtSignal()

    NAME_COL = 0
    TOKEN_COL = 1

    UpdateTimerPeriod = 2000

    def __init__(self, authenticator_keys: auth.AuthenticatorKeys, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._keys = authenticator_keys
        self.updateTimer = QtCore.QTimer()
        self.updateTimer.start(self.UpdateTimerPeriod)
        self.updateTimer.timeout.connect(self.updateTokens)

    def getKeysObject(self):
        return self._keys

    def rowCount(self, parent=None):
        return self._keys.get_size()

    def columnCount(self, parent=None):
        return 2

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                self.updateTimer.stop()
            if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
                all_names = sorted(list(self._keys.get_names()))
                if index.column() == self.NAME_COL:
                    return all_names[index.row()]
                if index.column() == self.TOKEN_COL:
                    try:
                        return str(self._keys.get_token(all_names[index.row()])).zfill(6)
                    except Exception as e:
                        return "<error: " + str(e) + ">"
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        return None

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        try:
            if index.column() == self.NAME_COL:
                if index.data() != value:
                    old_name = str(index.data())
                    new_name = str(value)
                    self._keys.set_secret(new_name, self._keys.get_secret(old_name))
                    self._keys.remove_secret(old_name)
                    self.dataChanged.emit(index, index)
                    return True
        finally:
            self.updateTimer.start(self.UpdateTimerPeriod)
        return False

    def headerData(self, rowcol, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if rowcol == self.NAME_COL:
                return "Name"
            if rowcol == self.TOKEN_COL:
                return "Token"
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)
        if index.isValid():
            l = sorted(list(self._keys.get_names()))
            if index.column() == self.NAME_COL:
                flags |= QtCore.Qt.ItemIsEditable
                flags |= QtCore.Qt.ItemIsSelectable
                flags |= QtCore.Qt.ItemIsEnabled
                return flags
            if index.column() == self.TOKEN_COL:
                return flags

        # flags |= QtCore.Qt.ItemIsEditable
        # flags |= QtCore.Qt.ItemIsSelectable
        # flags |= QtCore.Qt.ItemIsEnabled
        # flags |= QtCore.Qt.ItemIsDragEnabled
        # flags |= QtCore.Qt.ItemIsDropEnabled
        return flags

    def updateTokens(self):
        self.dataChanged.emit(self.index(1, 0), self.index(1, self._keys.get_size() - 1))
        self.tokensUpdatedSignal.emit()

    def refreshAll(self):
        self.beginResetModel()
        self.endResetModel()

    def removeRows(self, start_row, count, parent=None, *args, **kwargs):
        self.beginRemoveRows(QtCore.QModelIndex(), start_row, start_row + count - 1)
        to_remove = []
        for i in range(start_row, start_row + count):
            to_remove.append(self.data(self.index(i, self.NAME_COL), role=QtCore.Qt.DisplayRole))
        for name in to_remove:
            self._keys.remove_secret(name)
        self.endRemoveRows()
        return True
