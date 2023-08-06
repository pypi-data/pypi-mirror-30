from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, qApp
from PyQt5.Qt import QIcon
import os


class SamAuthenticatorTrayIcon(QSystemTrayIcon):
    IconTooltip_normal = "Sam Authenticator"

    def __init__(self, main_win, icon, parent=None):
        QSystemTrayIcon.__init__(self, parent)

        self.setIcon(icon)

        self.main_win = main_win
        self.menu = QMenu(parent)
        self.show_action = self.menu.addAction("Show")
        self.menu.addSeparator()
        self.exit_action = self.menu.addAction("Exit")
        self.setContextMenu(self.menu)
        self.exit_action.triggered.connect(qApp.quit)
        self.show_action.triggered.connect(self.main_win.raise_)
        self.setToolTip(self.IconTooltip_normal)
