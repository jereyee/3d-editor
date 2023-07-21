import json
import pickle
import sys
from PySide6.QtCore import Property, QObject, QPropertyAnimation, Signal, Qt, QTime
from PySide6.QtGui import QGuiApplication, QMatrix4x4, QQuaternion, QVector3D, QColor
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QPushButton, QListWidget, QLabel, QListWidgetItem, QComboBox,
                               QLineEdit, QColorDialog, QFormLayout, QDialog)
from editObject import EditWindow
from userInterface import UIWidget
from entityObject import Entity3D


class MainWindow(QMainWindow):
    """_summary_

    Args:
        QMainWindow (_type_): _description_

    Attributes:
        view (Qt3DExtras.Qt3DWindow): _description_
        container (QWidget): _description_
        size (QSize): _description_
        camController (Qt3DExtras.QOrbitCameraController): _description_
        rootEntity (Qt3DCore.QEntity): _description_
        entities (list): _description_
        selectedEntity (Entity3D): _description_
        editWindow (EditWindow): _description_

    Methods:
        createScene: _description_
        addShape: _description_
        addEntity: _description_
        deleteEntity: _description_
        updateEditButton: _description_
        openEditWindow: _description_
        closeEvent: _description_
        save_data: _description_
        load_data: _description_
    """
    def __init__(self):
        super().__init__()

        # Create the 3D window
        self.view = Qt3DExtras.Qt3DWindow()

        # Create a container for the 3D window
        container = QWidget.createWindowContainer(self.view)
        size = self.view.screen().size()
        container.setMinimumSize(size * 0.5)
        container.setMaximumSize(size)

        # Create a widget for the 3D window and the buttons
        widget = QWidget()
        layout = QHBoxLayout(widget)  # Change QVBoxLayout to QHBoxLayout

        # Add the 3D window container to the layout
        layout.addWidget(container, 1)

        # Create the UI widget and add it to the layout
        self.uiWidget = UIWidget()
        layout.addWidget(self.uiWidget)

        # Set the widget as the central widget of the window
        self.setCentralWidget(widget)

        # Create the 3D scene
        self.createScene()

        # Load entities from file
        self.entities = self.load_data('entities.json')

        # Restore all objects to the UI Widget
        if self.entities:
            for entity in self.entities:
                self.uiWidget.addToList(entity)

        # Store the selected entity, if any
        self.selectedEntity = None

        # Connect the buttons to their respective slots
        self.uiWidget.addButton.clicked.connect(self.addShape)
        self.uiWidget.deleteButton.clicked.connect(self.deleteEntity)
        self.uiWidget.editButton.clicked.connect(self.openEditWindow)

        # Connect the currentItemChanged signal to a slot
        self.uiWidget.entityWidgetList.currentItemChanged.connect(
            self.updateEditButton)

    def createScene(self):
        
        # Root entity
        self.rootEntity = Qt3DCore.QEntity()

        # Camera
        self.view.camera().setPosition(QVector3D(0, 0, 100))
        self.view.camera().setViewCenter(QVector3D(0, 0, 30))

        # For camera controls
        self.camController = Qt3DExtras.QOrbitCameraController(self.rootEntity)
        self.camController.setLinearSpeed(180)
        self.camController.setLookSpeed(180)
        self.camController.setCamera(self.view.camera())

        # Set the root entity of the scene
        self.view.setRootEntity(self.rootEntity)

    def addShape(self):
        # Get the selected shape
        selectedShape = self.uiWidget.shapeComboBox.currentText()

        # Mapping of shape names to their corresponding classes
        shape_classes = {
            "Cube": Qt3DExtras.QCuboidMesh,
            "Sphere": Qt3DExtras.QSphereMesh
        }

        # Create the shape
        shape_class = shape_classes.get(selectedShape)
        if shape_class is not None:
            self.addEntity(shape_class(), selectedShape)

    def addEntity(self, mesh, name):
        # Create an entity
        entity = Entity3D(self.rootEntity, mesh, name + str(len(self.entities) + 1))

        if name == "Cube":
            entity.mesh.setXExtent(10)
            entity.mesh.setYExtent(10)
            entity.mesh.setZExtent(10)
        elif name == "Sphere":
            entity.mesh.setRadius(5)

        entity.transform.setScale3D(QVector3D(1, 1, 1))  # Set scale
        entity.transform.setRotation(QQuaternion.fromAxisAndAngle(
            QVector3D(1, 0, 0), 45))  # Set rotation
        entity.transform.setTranslation(
            QVector3D(10 * len(self.entities), 0, 0))  # Set position

        # Add the entity to the UI widget
        self.uiWidget.addToList(entity)

        # Add the entity to the dictionary of entities
        self.entities.append(entity)

    def deleteEntity(self):
        # Get the selected item
        selectedItem = self.uiWidget.entityWidgetList.currentItem()

        # Remove the entity from the scene and the dictionary
        if selectedItem is not None:
            # Get the entity from the item's data
            selectedEntity = selectedItem.data(Qt.UserRole)
            self.entities.remove(selectedEntity)

            # Delete the entity
            selectedEntity.entity.deleteLater()

            # Remove the item from the widget list
            row = self.uiWidget.entityWidgetList.row(selectedItem)
            self.uiWidget.entityWidgetList.takeItem(row)

            # If the deleted entity was the selected one, set selectedEntity to None
            if self.selectedEntity == selectedEntity:
                self.selectedEntity = None

            # Update the state of the "Edit" button
            self.updateEditButton()

    def updateEditButton(self):
        # Enable the "Edit" button if an item is selected, disable it otherwise
        selectedItem = self.uiWidget.entityWidgetList.currentItem()
        self.uiWidget.editButton.setEnabled(selectedItem is not None)

        # Update selectedEntity
        if selectedItem is not None:
            self.selectedEntity = selectedItem.data(Qt.UserRole)
        else:
            self.selectedEntity = None

    def openEditWindow(self):
        # Open the edit window
        self.editWindow = EditWindow(self)
        self.editWindow.loadEntity(self.selectedEntity)
        self.editWindow.show()

    def closeEvent(self, event):
        # Save entities to file when the application is closing
        self.save_data(self.entities, 'entities.json')
        event.accept()

    def save_data(self, data, filename):
        with open(filename, 'w') as f:
            json.dump([entity.to_dict() for entity in data], f)

    def load_data(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                return [Entity3D.from_dict(d, self.rootEntity) for d in data]
        except (FileNotFoundError, EOFError, ValueError):
            return []


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
