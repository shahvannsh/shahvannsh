import sys
from PyQt5.QtWidgets import (QApplication,QMainWindow,QCheckBox)
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI WINDOW")
        self.checkBox = QCheckBox("Do you like Python?", self)
        self.checkBox.setGeometry(10,0,500,100)
        self.setGeometry(700,300,500,500)
        self.initUI()

    def initUI(self):
        self.checkBox.setGeometry(10,0,500,100)
        self.checkBox.setStyleSheet("front-size: 60px;"
                                    "front-family: Arial;")
        self.checkBox.setChecked(False)
        self.checkBox.stateChanged.connect(self.checkbox_changed)

    def checkbox_changed(self, state):
        if state == Qt.Checked:
            print("You like Python!")
        else:
            print("You don't like Python!")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()