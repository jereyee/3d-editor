
from PySide6.QtWidgets import (QColorDialog, QDialog,
                               QFormLayout, QLineEdit, QLabel,
                               QHBoxLayout, QDoubleSpinBox)
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender
from src.command import Command
from src.constants import STL_SCALE


class EditWindow(QDialog):
    """ 
    A class used to represent an Edit Window which allows for editing the attributes of a selected object.
    ...

    Attributes
    ----------
    editForm : QFormLayout
        a form layout for editing the selected object's attributes
    nameEdit : QLineEdit
        an input field for the name attribute
    colorLabel : QLabel
        a label for the color attribute
    positionXEdit, positionYEdit, positionZEdit : QLineEdit
        input fields for each component of the position attribute
    positionLayout : QHBoxLayout
        a layout for the position fields
    orientationWEdit, orientationXEdit, orientationYEdit, orientationZEdit : QLineEdit
        input fields for each component of the orientation attribute
    orientationLayout : QHBoxLayout
        a layout for the orientation fields
    dimensionXEdit, dimensionYEdit, dimensionZEdit : QLineEdit
        input fields for each dimension of the object
    dimensionLayout : QHBoxLayout
        a layout for the dimension fields
    selectedEntity : Entity3D
        an instance of the Entity3D class
    history : list
        a list to keep track of the changes
    history_index : int
        an index to keep track of the current state in the history

    Methods
    -------
    createSpinBox(min_val, max_val, step):
        Creates a spin box with the given parameters
    executeCommand(data):
        Executes a command to update the selected entity's data
    applyNameChange():
        Applies a change to the name of the selected entity
    applyPositionChange():
        Applies a change to the position of the selected entity
    applyOrientationChange():
        Applies a change to the orientation of the selected entity
    applyDimensionChange():
        Applies a change to the dimensions of the selected entity
    openColorPicker(event):
        Opens a color picker dialog
    updateColorLabel(color):
        Updates the color label with the given color
    blockOrUnblockSignals(block):
        Blocks or unblocks the signals of the input fields
    loadEntity(entity):
        Loads an entity into the edit window
    undo():
        Undoes the last change
    redo():
        Redoes the last undone change
    """

    def __init__(self, mainWindow, parent=None):
        super().__init__(parent)

        self.mainWindow = mainWindow

        self.setWindowTitle("Edit Object")

        # Create a form for editing the selected object's attributes
        self.editForm = QFormLayout(self)

        # Create input fields for the attributes
        self.nameEdit = QLineEdit()

        # Create a label for the color
        self.colorLabel = QLabel()
        self.colorLabel.setAutoFillBackground(True)
        self.colorLabel.mousePressEvent = self.openColorPicker

        # Create separate input fields for each component of the position
        self.positionXEdit = self.createSpinBox(-100.0, 100.0, 1)
        self.positionYEdit = self.createSpinBox(-100.0, 100.0, 1)
        self.positionZEdit = self.createSpinBox(-100.0, 100.0, 1)

        # Create a QHBoxLayout for the position fields
        self.positionLayout = QHBoxLayout()
        self.positionLayout.addWidget(self.positionXEdit)
        self.positionLayout.addWidget(self.positionYEdit)
        self.positionLayout.addWidget(self.positionZEdit)

        # Create separate input fields for each component of the orientation
        self.orientationWEdit = self.createSpinBox(-1.0, 1.0, 0.05)
        self.orientationXEdit = self.createSpinBox(-1.0, 1.0, 0.05)
        self.orientationYEdit = self.createSpinBox(-1.0, 1.0, 0.05)
        self.orientationZEdit = self.createSpinBox(-1.0, 1.0, 0.05)

        # Create a QHBoxLayout for the orientation fields
        self.orientationLayout = QHBoxLayout()
        self.orientationLayout.addWidget(self.orientationWEdit)
        self.orientationLayout.addWidget(self.orientationXEdit)
        self.orientationLayout.addWidget(self.orientationYEdit)
        self.orientationLayout.addWidget(self.orientationZEdit)

        # Create separate input fields for each dimension of the object
        self.dimensionXEdit = self.createSpinBox(0.0, 100.0, 1)
        self.dimensionYEdit = self.createSpinBox(0.0, 100.0, 1)
        self.dimensionZEdit = self.createSpinBox(0.0, 100.0, 1)

        # Create a QHBoxLayout for the dimension fields
        self.dimensionLayout = QHBoxLayout()
        self.dimensionLayout.addWidget(self.dimensionXEdit)
        self.dimensionLayout.addWidget(self.dimensionYEdit)
        self.dimensionLayout.addWidget(self.dimensionZEdit)

        # Add the input fields to the form
        self.editForm.addRow("Name:", self.nameEdit)
        self.editForm.addRow("Color:", self.colorLabel)
        self.editForm.addRow("Position:", self.positionLayout)
        self.editForm.addRow("Orientation:", self.orientationLayout)
        self.editForm.addRow("Dimensions:", self.dimensionLayout)

        # Create a list to keep track of the changes
        self.history = []
        self.history_index = -1

        # Connect the editingFinished signals to the applyChanges methods
        """ Should use valueChanged for more real-time updates, but there currently is a bug.
        When the program starts, the valueChanged signals are emitted, which causes the entity to be updated.
        """
        self.nameEdit.editingFinished.connect(self.applyNameChange)
        self.positionXEdit.valueChanged.connect(self.applyPositionChange)
        self.positionYEdit.valueChanged.connect(self.applyPositionChange)
        self.positionZEdit.valueChanged.connect(self.applyPositionChange)
        self.orientationWEdit.valueChanged.connect(
            self.applyOrientationChange)
        self.orientationXEdit.valueChanged.connect(
            self.applyOrientationChange)
        self.orientationYEdit.valueChanged.connect(
            self.applyOrientationChange)
        self.orientationZEdit.valueChanged.connect(
            self.applyOrientationChange)
        self.dimensionXEdit.valueChanged.connect(self.applyDimensionChange)
        self.dimensionYEdit.valueChanged.connect(self.applyDimensionChange)
        self.dimensionZEdit.valueChanged.connect(self.applyDimensionChange)

    def createSpinBox(self, min_val, max_val, step):
        spin_box = QDoubleSpinBox()
        spin_box.setRange(min_val, max_val)
        spin_box.setSingleStep(step)
        return spin_box

    def executeCommand(self, data):
        # Create a command to update the selected entity's data
        command = Command(self.selectedEntity, data)
        command.execute()

        # Add it to the history
        self.history = self.history[:self.history_index+1]
        self.history.append(command)
        self.history_index += 1

    def applyNameChange(self):
        if self.nameEdit.signalsBlocked():
            return None
        # Get the new name from the input field
        name = self.nameEdit.text()

        if name == self.selectedEntity.name:
            return

        # Create a command to update the selected entity's name
        self.executeCommand({'name': name})

        # Update the text of the QListWidgetItem
        self.mainWindow.uiWidget.entityWidgetList.currentItem().setText(name)

    def applyPositionChange(self):
        if self.positionXEdit.signalsBlocked():
            return None
        # Get the new position
        positionX = self.positionXEdit.value()
        positionY = self.positionYEdit.value()
        positionZ = self.positionZEdit.value()
        position = (positionX, positionY, positionZ)

        # Create a command to update the selected entity's position
        self.executeCommand({'position': position})

    def applyOrientationChange(self):
        # Get the new orientation
        orientationW = self.orientationWEdit.value()
        orientationX = self.orientationXEdit.value()
        orientationY = self.orientationYEdit.value()
        orientationZ = self.orientationZEdit.value()
        orientation = (orientationW, orientationX, orientationY, orientationZ)

        # Create a command to update the selected entity's orientation
        self.executeCommand({'orientation': orientation})

    def applyDimensionChange(self):
        # Get the new dimensions
        dimensionX = self.dimensionXEdit.value()
        dimensionY = self.dimensionYEdit.value()
        dimensionZ = self.dimensionZEdit.value()
        dimensions = (dimensionX, dimensionY, dimensionZ)

        # Create a command to update the selected entity's dimensions
        self.executeCommand({'dimensions': dimensions})

    def openColorPicker(self, event):
        color = QColorDialog.getColor(self.selectedEntity.material.diffuse())
        if color.isValid():
            self.updateColorLabel(color)

            # Create a command to update the selected entity's color
            self.executeCommand({'color': color.getRgb()})

    def updateColorLabel(self, color):
        palette = self.colorLabel.palette()
        palette.setColor(self.colorLabel.backgroundRole(), color)
        self.colorLabel.setPalette(palette)

    def blockOrUnblockSignals(self, block):
        # Block the signals of the input fields
        self.nameEdit.blockSignals(block)
        self.positionXEdit.blockSignals(block)
        self.positionYEdit.blockSignals(block)
        self.positionZEdit.blockSignals(block)
        self.orientationWEdit.blockSignals(block)
        self.orientationXEdit.blockSignals(block)
        self.orientationYEdit.blockSignals(block)
        self.orientationZEdit.blockSignals(block)
        self.dimensionXEdit.blockSignals(block)
        self.dimensionYEdit.blockSignals(block)
        self.dimensionZEdit.blockSignals(block)

    def loadEntity(self, entity):
        self.selectedEntity = entity

        # Block the signals of the input fields
        self.blockOrUnblockSignals(True)

        # Update the input fields with the selected entity's attributes
        self.nameEdit.setText(self.selectedEntity.name)

        # Update the color label
        color = self.selectedEntity.material.diffuse()
        self.updateColorLabel(color)

        # Update the position fields
        position = self.selectedEntity.transform.translation()
        self.positionXEdit.setValue(position.x())
        self.positionYEdit.setValue(position.y())
        self.positionZEdit.setValue(position.z())

        # Update the orientation fields
        orientation = self.selectedEntity.transform.rotation()
        self.orientationWEdit.setValue(orientation.scalar())
        self.orientationXEdit.setValue(orientation.x())
        self.orientationYEdit.setValue(orientation.y())
        self.orientationZEdit.setValue(orientation.z())

        # Update the dimension fields
        if isinstance(self.selectedEntity.mesh, Qt3DExtras.QCuboidMesh):
            self.dimensionXEdit.setValue(self.selectedEntity.mesh.xExtent())
            self.dimensionYEdit.setValue(self.selectedEntity.mesh.yExtent())
            self.dimensionZEdit.setValue(self.selectedEntity.mesh.zExtent())
            self.dimensionYEdit.setVisible(True)
            self.dimensionZEdit.setVisible(True)
        elif isinstance(self.selectedEntity.mesh, Qt3DExtras.QSphereMesh):
            self.dimensionXEdit.setValue(self.selectedEntity.mesh.radius())
            self.dimensionYEdit.setValue(0)
            self.dimensionZEdit.setValue(0)
            self.dimensionYEdit.setVisible(False)
            self.dimensionZEdit.setVisible(False)
        elif isinstance(self.selectedEntity.mesh, Qt3DRender.QMesh):
            self.dimensionXEdit.setValue(
                self.selectedEntity.transform.scale3D().x() * (1/STL_SCALE))
            self.dimensionYEdit.setValue(
                self.selectedEntity.transform.scale3D().y() * (1/STL_SCALE))
            self.dimensionZEdit.setValue(
                self.selectedEntity.transform.scale3D().z() * (1/STL_SCALE))
            self.dimensionYEdit.setVisible(True)
            self.dimensionZEdit.setVisible(True)

        # Unblock the signals of the input fields
        self.blockOrUnblockSignals(False)

    def undo(self):
        """ TODO: There's a bug here where the undo throws an error when the object has already been deleted """
        if self.history_index >= 0:
            self.history[self.history_index].undo()
            self.history_index -= 1

            # Update the values in the EditWindow
            self.loadEntity(self.selectedEntity)

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.history[self.history_index].execute()

            # Update the values in the EditWindow
            self.loadEntity(self.selectedEntity)
