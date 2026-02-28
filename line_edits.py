import sys
from PyQt5.QtWidgets import (QApplication,QMainWindow,QLineEdit,QPushButton)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(700,300,500,500)
        self.setWindowTitle("QLineEdit")
        self.lineEdit = QLineEdit(self)
        self.button = QPushButton("Submit",self)
        self.initUI()

    def initUI(self):
        self.lineEdit.setGeometry(10,10,200,40)
        self.button.setGeometry(210,10,100,40)
        self.button.setStyleSheet("font-size:25px;"
                                    "font-family:Arial;")
        self.lineEdit.setStyleSheet("font-size:25px;"
                                    "font-family:Arial;")
        self.lineEdit.setPlaceholderText("Enter your name")

        self.button.clicked.connect(self.submit)
    def submit(self):
        text = self.lineEdit.text()
        print(f"Hello {text}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
