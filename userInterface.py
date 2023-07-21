from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QPushButton, QListWidget, QLabel, QListWidgetItem, QComboBox,
                               QLineEdit, QColorDialog, QFormLayout, QDialog)
from PySide6.QtCore import Qt

class UIWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a vertical layout for the list and buttons
        self.layout = QVBoxLayout(self)

        # Create a list to keep track of the objects
        self.entityWidgetList = QListWidget()
        self.layout.addWidget(self.entityWidgetList)

        # Create a label for the combo box
        self.shapeLabel = QLabel("Select shape to add:")
        self.layout.addWidget(self.shapeLabel)

        # Create a combo box for selecting the shape to add
        self.shapeComboBox = QComboBox()
        self.shapeComboBox.addItem("Cube")
        self.shapeComboBox.addItem("Sphere")
        self.layout.addWidget(self.shapeComboBox)

        # Create a button to add shapes
        self.addButton = QPushButton("Add object")
        self.layout.addWidget(self.addButton)

        # Create a button to delete entities
        self.deleteButton = QPushButton("Delete object")
        self.layout.addWidget(self.deleteButton)

        # Create an edit button
        self.editButton = QPushButton("Edit object")
        self.editButton.setEnabled(False)  # Initially disabled
        self.layout.addWidget(self.editButton)

    def addToList(self, entity):
        # Add an entity to the list
        entityItem = QListWidgetItem(entity.name)
        entityItem.setData(Qt.UserRole, entity)
        self.entityWidgetList.addItem(entityItem)
        