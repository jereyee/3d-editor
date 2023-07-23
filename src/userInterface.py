from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QPushButton, QListWidget, QLabel, QListWidgetItem, QComboBox,
                               QLineEdit, QColorDialog, QFormLayout, QDialog)
from PySide6.QtCore import Qt

class UIWidget(QWidget):
    """ 
    A class used to represent a UI Widget which includes a list of objects and buttons for manipulating them.
    ...

    Attributes
    ----------
    layout : QVBoxLayout
        a vertical layout for the list and buttons
    entityWidgetList : QListWidget
        a list widget to keep track of the objects
    shapeLabel : QLabel
        a label for the shape selection combo box
    shapeComboBox : QComboBox
        a combo box for selecting the shape to add
    addButton : QPushButton
        a button to add shapes
    deleteButton : QPushButton
        a button to delete entities
    undoButton : QPushButton
        a button to undo the last change
    redoButton : QPushButton
        a button to redo the last undone change

    Methods
    -------
    addToList(entity):
        Adds an entity to the list
    """
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
        self.shapeComboBox.addItem("STL")
        self.layout.addWidget(self.shapeComboBox)

        # Create a button to add shapes
        self.addButton = QPushButton("Add object")
        self.layout.addWidget(self.addButton)

        # Create a button to delete entities
        self.deleteButton = QPushButton("Delete object")
        self.layout.addWidget(self.deleteButton)

        # Create undo and redo buttons
        """ TODO: Buttons should be disabled when there is nothing to undo or redo """
        self.undoButton = QPushButton("Undo")
        self.layout.addWidget(self.undoButton)

        self.redoButton = QPushButton("Redo")
        self.layout.addWidget(self.redoButton)

    def addToList(self, entity):
        # Add an entity to the list
        entityItem = QListWidgetItem(entity.name)
        entityItem.setData(Qt.UserRole, entity)
        self.entityWidgetList.addItem(entityItem)
        self.entityWidgetList.setCurrentItem(entityItem)
        