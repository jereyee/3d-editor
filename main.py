import sys
from PySide6.QtWidgets import (QApplication)

from src.mainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.setWindowTitle("3D Model Editor")
    mainWindow.show()
    sys.exit(app.exec())
