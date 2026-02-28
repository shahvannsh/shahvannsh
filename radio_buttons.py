import sys
from PyQt5.QtWidgets import (QApplication,QMainWindow,QRadioButton,QButtonGroup)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(700,300,500,500)
        self.radio1 = QRadioButton("Visa", self)
        self.radio2 = QRadioButton("Mastercard", self)
        self.radio3 = QRadioButton("Gift card", self)
        self.radio4 = QRadioButton("In-store", self)
        self.radio5 = QRadioButton("online", self)
        self.buttonGroup1 = QButtonGroup(self)
        self.buttonGroup2 = QButtonGroup(self)
        self.initUI()

    def initUI(self):
        self.radio1.setGeometry(0,0,300,500)
        self.radio2.setGeometry(0,50,300,500)
        self.radio3.setGeometry(0,100,300,500)
        self.radio4.setGeometry(0,150,300,500)
        self.radio5.setGeometry(0,200,300,500)

        self.buttonGroup1.addButton(self.radio1)
        self.buttonGroup1.addButton(self.radio2)
        self.buttonGroup1.addButton(self.radio3)
        self.buttonGroup2.addButton(self.radio4)
        self.buttonGroup2.addButton(self.radio5)

        self.setStyleSheet("QRadioButton{ "
                           "padding: 10px;"
                           "font-size: 40px;"
                           "font-weight: bold;"
                           "font-family: Arial; }")
        self.radio1.toggled.connect(self.radio_button_changed)
        self.radio2.toggled.connect(self.radio_button_changed)
        self.radio3.toggled.connect(self.radio_button_changed)
        self.radio4.toggled.connect(self.radio_button_changed)
        self.radio5.toggled.connect(self.radio_button_changed)

    def radio_button_changed(self):
        radio_button = self.sender()
        if radio_button.isChecked():
            print(f"{radio_button.text()} is selected")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())