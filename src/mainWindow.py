import json
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QQuaternion, QVector3D, QColor
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QLabel)
from src.editWindow import EditWindow
from src.userInterface import UIWidget
from src.entityObject import Entity3D
from src.constants import PERSPECTIVE_PROJECTION_VALUES, STL_SCALE, ShapeType, shapeClasses, STL_FILE_PATH


class MainWindow(QMainWindow):
    """
    The MainWindow class is the main application window that contains the 3D view, UI widgets, and the edit window.

    Attributes
    ----------
    view : Qt3DExtras.Qt3DWindow
        The 3D window for displaying the 3D scene.
    uiWidget : UIWidget
        The widget that contains the user interface controls.
    editWindow : EditWindow
        The window for editing the properties of the selected entity.
    rootEntity : Qt3DCore.QEntity
        The root entity of the 3D scene.
    entities : list
        A list of all entities in the scene.
    previousMousePosition : QVector3D
        The previous position of the mouse.
    mousePressed : bool
        A flag indicating whether the mouse button is currently pressed.
    selectedEntity : Entity3D
        The currently selected entity in the scene.

    Methods
    -------
    onMousePressed(event):
        Handles the mouse press event.
    onMouseReleased(event):
        Handles the mouse release event.
    onMouseMoved(event):
        Handles the mouse move event.
    updateCameraPosition():
        Updates the label displaying the camera position.
    onEntityClicked(entity):
        Handles the event when an entity is clicked.
    createScene():
        Creates the 3D scene.
    addShape():
        Adds a new shape to the scene based on the selected shape in the UI widget.
    addEntity(mesh, shape):
        Adds a new entity to the scene.
    deleteEntity():
        Deletes the selected entity from the scene.
    updateEditButton():
        Updates the state of the "Edit" button.
    openEditWindow():
        Opens the edit window for the selected entity.
    closeEvent(event):
        Handles the event when the application is closing.
    save_data(data, filename):
        Saves the entities to a file.
    load_data(filename):
        Loads the entities from a file.
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
        mainLayout = QHBoxLayout(widget)  # Main layout

        # Create a QVBoxLayout for the 3D window and the camera position label
        vLayout = QVBoxLayout()
        self.cameraPositionLabel = QLabel("Camera Position: ")
        vLayout.addWidget(container, 1)
        vLayout.addWidget(self.cameraPositionLabel)

        # Add the QVBoxLayout to the main layout
        mainLayout.addLayout(vLayout, 1)

        # Create a QVBoxLayout for the UI widget and edit window
        vSideLayout = QVBoxLayout()

        # Create the UI widget and add it to the main layout
        self.uiWidget = UIWidget()
        vSideLayout.addWidget(self.uiWidget)

        # Create an edit window and add it to the main layout
        self.editWindow = EditWindow(self)
        vSideLayout.addWidget(self.editWindow)
        self.editWindow.hide()  # Initially hidden

        # Add both the UI Widget and Edit Window to the layout
        mainLayout.addLayout(vSideLayout)

        # Set the widget as the central widget of the window
        self.setCentralWidget(widget)

        # Create the 3D scene
        self.createScene()

        # Create a timer to update the camera position label
        self.view.camera().positionChanged.connect(self.updateCameraPosition)

        # Load entities from file
        self.entities = self.load_data('entities.json')

        # Store the previous mouse position
        self.previousMousePosition = QVector3D()
        self.mousePressed = False

        # Store the selected entity
        self.selectedEntity = None

        # Connect the buttons to their respective slots
        self.uiWidget.addButton.clicked.connect(self.addShape)
        self.uiWidget.deleteButton.clicked.connect(self.deleteEntity)
        # self.uiWidget.editButton.clicked.connect(self.openEditWindow)

        # Connect the currentItemChanged signal to a slot
        self.uiWidget.entityWidgetList.currentItemChanged.connect(
            self.updateEditButton)

        # Connect the undo and redo buttons to the undo and redo methods of the EditWindow
        self.uiWidget.undoButton.clicked.connect(self.editWindow.undo)
        self.uiWidget.redoButton.clicked.connect(self.editWindow.redo)

        # Restore all objects to the UI Widget
        if self.entities:
            for entity in self.entities:
                self.uiWidget.addToList(entity)

    def onMousePressed(self, event):
        self.mousePressed = True
        self.camController.setEnabled(False)
        self.previousMousePosition = event.worldIntersection()
        self.initialZ = self.previousMousePosition.z()

    def onMouseReleased(self, event):
        self.mousePressed = False
        self.camController.setEnabled(True)

    def onMouseMoved(self, event):
        """ When I keep swinging the mouse around, the object gets smaller and smaller. Why? """
        # Get the world position of the mouse click
        world_position = event.worldIntersection()

        if self.mousePressed:
            # If an entity is selected, calculate the new position of the entity
            if self.selectedEntity is not None:
                # Calculate the difference between the current and previous mouse positions
                difference = QVector3D(world_position.x() - self.previousMousePosition.x(),
                                       world_position.y() - self.previousMousePosition.y(),
                                       world_position.z() - self.previousMousePosition.z()) 

                # Apply the difference to the entity's position
                new_position = self.selectedEntity.transform.translation() + difference

                # Clamp the z position to [-10, 10]
                # new_position.setZ(max(min(new_position.z(), 10), -10))
                self.selectedEntity.transform.setTranslation(new_position)

                self.editWindow.loadEntity(self.selectedEntity)

            # Update the previous mouse position
            self.previousMousePosition = world_position

    def updateCameraPosition(self):
        # Update the camera position label
        camera_position = self.view.camera().position()
        self.cameraPositionLabel.setText(
            f"Camera position: x={camera_position.x():.2f}, y={camera_position.y():.2f}, z={camera_position.z():.2f}")

    def onEntityClicked(self, entity):
        # Find the corresponding item in the list and select it
        for i in range(self.uiWidget.entityWidgetList.count()):
            item = self.uiWidget.entityWidgetList.item(i)
            if item.data(Qt.UserRole) is entity:
                self.uiWidget.entityWidgetList.setCurrentItem(item)
                break

    def createScene(self):

        # Root entity
        self.rootEntity = Qt3DCore.QEntity()

        # Set the background for the frame
        self.view.defaultFrameGraph().setClearColor(QColor(Qt.gray))

        # Camera
        self.view.camera().lens().setPerspectiveProjection(*PERSPECTIVE_PROJECTION_VALUES)
        self.view.camera().setViewCenter(QVector3D(0, 0, 0))
        self.view.camera().setPosition(QVector3D(0, 0, 10))
        self.view.camera().setUpVector(QVector3D(0, 1, 0))

        # For camera controls
        self.camController = Qt3DExtras.QOrbitCameraController(self.rootEntity)
        self.camController.setLinearSpeed(90)
        self.camController.setLookSpeed(180)
        self.camController.setCamera(self.view.camera())

        # Set the root entity of the scene
        self.view.setRootEntity(self.rootEntity)

    def addShape(self):
        # Get the selected shape
        selectedShape = ShapeType[self.uiWidget.shapeComboBox.currentText().upper()]

        # Create the shape
        shape_class = shapeClasses.get(selectedShape)
        if shape_class is not None:
            if selectedShape == ShapeType.STL:
                # If the selected shape is STL, load the STL file
                mesh = shape_class()
                mesh.setSource(QUrl.fromLocalFile(STL_FILE_PATH))
                self.addEntity(mesh, selectedShape)
            else:
                self.addEntity(shape_class(), selectedShape)

    def addEntity(self, mesh, shape):
        # Create an entity
        entity = Entity3D(self.rootEntity, mesh, shape.value +
                          str(len(self.entities) + 1), self)

        if shape == ShapeType.CUBE:
            entity.mesh.setXExtent(1)
            entity.mesh.setYExtent(1)
            entity.mesh.setZExtent(1)
        elif shape == ShapeType.SPHERE:
            entity.mesh.setRadius(1)

        scale = QVector3D(STL_SCALE, STL_SCALE,
                          STL_SCALE) if shape == ShapeType.STL else QVector3D(1, 1, 1)
        rotation = QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 45)
        position = QVector3D(3 * len(self.entities), 0, 0)

        entity.setup(scale, rotation, position)

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
        # self.uiWidget.editButton.setEnabled(selectedItem is not None)

        # Update selectedEntity
        if selectedItem is not None:
            self.selectedEntity = selectedItem.data(Qt.UserRole)
            self.openEditWindow()
        else:
            self.selectedEntity = None

    def openEditWindow(self):
        # Show the edit window if an entity is selected, hide it otherwise
        if self.selectedEntity is not None:
            self.editWindow.loadEntity(self.selectedEntity)
            self.editWindow.show()
        else:
            self.editWindow.hide()

    def closeEvent(self, event):
        # Save entities to file when the application is closing
        self.save_data(self.entities, 'entities.json')
        event.accept()

    def save_data(self, data, filename):
        with open(filename, 'w') as f:
            json.dump([entity.toDict() for entity in data], f)

    def load_data(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                entities = [Entity3D.fromDict(
                    d, self.rootEntity, self) for d in data]
                return entities
        except (FileNotFoundError, EOFError, ValueError) as e:
            print(f"Error loading data from {filename}: {e}")
            return []
