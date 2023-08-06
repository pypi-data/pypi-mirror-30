from PyQt5.QtWidgets import QApplication
import SamAuthenticator.AuthenticatorWindow as MainWindow
import sys


def start():
    app = QApplication(sys.argv)

    w = MainWindow.AuthenticatorGUI()

    w.show()

    return app.exec_()
