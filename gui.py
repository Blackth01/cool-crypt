import os
import sys
import glob
import threading

from cryptography.fernet import InvalidToken

from crypttools.key_generator import derive_key
from crypttools.crypt_manager import encrypt
from crypttools.crypt_manager import decrypt

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, \
    QPushButton, QComboBox, QLineEdit, \
        QMessageBox, QFileDialog
from PyQt5 import uic


class Worker(QObject):
    updateStatusLabel = pyqtSignal(str)
    showMsg = pyqtSignal(str, bool)
    finished = pyqtSignal(str, bool)

    def start_cryptographic_action(self, directory, mode, key):
        error = False
        for filepath in glob.iglob("{}/**/*".format(directory), recursive=True):
            if(os.path.isfile(filepath)):
                if(mode == "Encrypt"):
                    if not self.encryptFile(filepath, key):
                        error = True
                        break
                else:
                    if not self.decryptFile(filepath, key):
                        error = True
                        break

        self.finished.emit(mode, error)


    def encryptFile(self, filepath, key):
        if(filepath[-6:] != ".enctb"):
            self.updateStatusLabel.emit("Encrypting: {}".format(filepath))
            try:
                encrypt(key, filepath, filepath+".enctb")
                os.remove(filepath)
                return True
            except Exception as e:
                self.showMsg.emit("An error occured while encrypting file {}. Error: {}".format(filepath, str(e)))
                return False

    def decryptFile(self, filepath, key):
        if(filepath[-6:] == ".enctb"):
            self.updateStatusLabel.emit("Decrypting: {}".format(filepath))
            try:
                decrypt(key, filepath, filepath[0:-6])
                self.remove_file(filepath, ignore_errors=False)
                return True
            except InvalidToken:
                self.remove_file(filepath[0:-6], ignore_errors=True)
                self.showMsg.emit("Can't decrypt the files! Please check if the password is right.", True)
                return False
            except Exception as e:
                self.remove_file(filepath[0:-6], ignore_errors=True)
                self.showMsg.emit("An error occured while decrypting file {}. Error: {}".format(filepath, str(e)), True)
                return False

    def remove_file(self, filepath, ignore_errors=False):
        if(ignore_errors):
            try:
                os.remove(filepath)
            except OSError:
                pass
        else:
            os.remove(filepath)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("main.ui", self)

        self.password_input = self.findChild(QLineEdit, "passwordInput")
        self.confirm_password_input = self.findChild(QLineEdit, "confirmPasswordInput")

        self.action_mode = self.findChild(QComboBox, "actionMode")
        self.action_button = self.findChild(QPushButton, "actionButton")
        self.select_directory_button = self.findChild(QPushButton, "selectDirectory")
        self.status_label = self.findChild(QLabel, "statusLabel")
        self.label_directory = self.findChild(QLabel, "labelDirectory")

        self.action_button.clicked.connect(self.executeAction)
        self.select_directory_button.clicked.connect(self.chooseDirectory)
        self.action_mode.currentTextChanged.connect(self.changeButtonText)

        self.directory_selected = ""

        self.worker = Worker()
        self.worker.finished.connect(self.actionFinished)
        self.worker.updateStatusLabel.connect(self.updateStatusLabel)
        self.worker.showMsg.connect(self.showMsg)

        self.show()


    def showMsg(self, msgText, error=True):
        msg = QMessageBox()
        if(error):
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
        else:
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Message")

        msg.setText(msgText)
        msg.exec_()


    def chooseDirectory(self):
        directory = str(QFileDialog.getExistingDirectory(self, "Select a directory"))
        if(not directory):
            self.label_directory.setText("No directory selected yet")
            self.directory_selected = ""
        else:
            self.label_directory.setText(directory)
            self.directory_selected = directory


    def changeButtonText(self, currentText):
        self.action_button.setText(currentText)
        if(currentText == "Encrypt"):
            self.updateStatusLabel("Waiting to encrypt the directory")
        else:
            self.updateStatusLabel("Waiting to decrypt the directory")


    def actionFinished(self, mode, error=False):
        if(mode == "Encrypt"):
            if not error:
                self.showMsg("The directory was encrypted successfully", error=False)
            self.updateStatusLabel("Waiting to encrypt the directory")
        else:
            if not error:
                self.showMsg("The directory was decrypted successfully", error=False)
            self.updateStatusLabel("Waiting to decrypt the directory")

        self.action_button.setEnabled(True)


    def executeAction(self):
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        directory = self.directory_selected

        if(not password):
            self.showMsg("No password was informed!")
            return False

        if(password != confirm_password):
            self.showMsg("Password inputs do not match!")
            return False

        if(not self.directory_selected):
            self.showMsg("No directory was selected!")
            return False

        passphrase = password.encode()

        key = derive_key(passphrase)

        mode = self.action_mode.currentText()

        #Disabling action button
        self.action_button.setEnabled(False)

        thread = threading.Thread(target=self.worker.start_cryptographic_action, args=(directory, mode,key))
        thread.start()

    def updateStatusLabel(self, text):
        self.status_label.setText(text)


app = QApplication(sys.argv)
window = MainWindow()
app.exec_()