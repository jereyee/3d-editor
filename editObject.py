from PySide6.QtWidgets import (QColorDialog, QDialog,
                               QFormLayout, QLineEdit, QLabel,
                               QPushButton, QHBoxLayout, QDoubleSpinBox)
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtGui import QGuiApplication, QMatrix4x4, QQuaternion, QVector3D, QColor

from entityObject import Entity3D


class Command:
    """ Currently, this only supports undo-ing changes to the name, color, position, and orientation of an entity.
    This also does not account for dragging the object.
    In the future, it could possibly support undo-ing adding an object to the scene, deleting an object from the scene, etc.
    """

    def __init__(self, entity, data):
        self.entity = entity
        self.previousData = entity.to_dict()
        self.currentData = data

    def execute(self):
        if self.entity is not None and self.entity.entity is not None:
            self.entity.update_properties(self.currentData)

    def undo(self):
        if self.entity is not None and self.entity.entity is not None:
            self.entity.update_properties(self.previousData)


class EditWindow(QDialog):
    """_summary_

    Args:
        QDialog (_type_): _description_

    Attributes:
        editForm (QFormLayout): _description_
        nameEdit (QLineEdit): _description_
        colorEdit (QColorDialog): _description_
        positionXEdit (QLineEdit): _description_
        positionYEdit (QLineEdit): _description_
        positionZEdit (QLineEdit): _description_
        positionLayout (QHBoxLayout): _description_
        orientationWEdit (QLineEdit): _description_
        orientationXEdit (QLineEdit): _description_
        orientationYEdit (QLineEdit): _description_
        orientationZEdit (QLineEdit): _description_
        orientationLayout (QHBoxLayout): _description_
        dimensionXEdit (QLineEdit): _description_
        dimensionYEdit (QLineEdit): _description_
        dimensionZEdit (QLineEdit): _description_
        dimensionLayout (QHBoxLayout): _description_
        saveButton (QPushButton): _description_
        selectedEntity (Entity3D): _description_
        history (list): _description_
        history_index (int): _description_

    Methods:
        loadEntity: _description_
        applyNameChange: _description_
        applyPositionChange: _description_
        applyOrientationChange: _description_
        applyDimensionChange: _description_
        updateColorLabel: _description_
        openColorPicker: _description_
        undo: _description_
        redo: _description_
    """

    def __init__(self, parent=None):
        super().__init__(parent)

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
        self.positionXEdit = QDoubleSpinBox()
        self.positionYEdit = QDoubleSpinBox()
        self.positionZEdit = QDoubleSpinBox()

        # Set the range of the QDoubleSpinBox widgets
        self.positionXEdit.setRange(-100.0, 100.0)
        self.positionYEdit.setRange(-100.0, 100.0)
        self.positionZEdit.setRange(-100.0, 100.0)

        # Create a QHBoxLayout for the position fields
        self.positionLayout = QHBoxLayout()
        self.positionLayout.addWidget(self.positionXEdit)
        self.positionLayout.addWidget(self.positionYEdit)
        self.positionLayout.addWidget(self.positionZEdit)

        # Create separate input fields for each component of the orientation
        self.orientationWEdit = QDoubleSpinBox()
        self.orientationXEdit = QDoubleSpinBox()
        self.orientationYEdit = QDoubleSpinBox()
        self.orientationZEdit = QDoubleSpinBox()

        # Set the range of the QDoubleSpinBox widgets
        self.orientationWEdit.setRange(-1.0, 1.0)
        self.orientationXEdit.setRange(-1.0, 1.0)
        self.orientationYEdit.setRange(-1.0, 1.0)
        self.orientationZEdit.setRange(-1.0, 1.0)

        # Create a QHBoxLayout for the orientation fields
        self.orientationLayout = QHBoxLayout()
        self.orientationLayout.addWidget(self.orientationWEdit)
        self.orientationLayout.addWidget(self.orientationXEdit)
        self.orientationLayout.addWidget(self.orientationYEdit)
        self.orientationLayout.addWidget(self.orientationZEdit)

        # Create separate input fields for each dimension of the object
        self.dimensionXEdit = QDoubleSpinBox()
        self.dimensionYEdit = QDoubleSpinBox()
        self.dimensionZEdit = QDoubleSpinBox()

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
        self.nameEdit.editingFinished.connect(self.applyNameChange)
        self.positionXEdit.editingFinished.connect(self.applyPositionChange)
        self.positionYEdit.editingFinished.connect(self.applyPositionChange)
        self.positionZEdit.editingFinished.connect(self.applyPositionChange)
        self.orientationWEdit.editingFinished.connect(
            self.applyOrientationChange)
        self.orientationXEdit.editingFinished.connect(
            self.applyOrientationChange)
        self.orientationYEdit.editingFinished.connect(
            self.applyOrientationChange)
        self.orientationZEdit.editingFinished.connect(
            self.applyOrientationChange)
        self.dimensionXEdit.editingFinished.connect(self.applyDimensionChange)
        self.dimensionYEdit.editingFinished.connect(self.applyDimensionChange)
        self.dimensionZEdit.editingFinished.connect(self.applyDimensionChange)

    def applyNameChange(self):
        # Get the new name from the input field
        name = self.nameEdit.text()

        # Create a command to update the selected entity's name
        command = Command(self.selectedEntity, {'name': name})
        command.execute()

        # Add it to the history
        self.history = self.history[:self.history_index+1]
        self.history.append(command)
        self.history_index += 1

        # Update the text of the QListWidgetItem
        self.selectedEntity.mainWindow.uiWidget.entityWidgetList.currentItem().setText(name)

    def applyPositionChange(self):
        # Get the new position
        positionX = self.positionXEdit.value()
        positionY = self.positionYEdit.value()
        positionZ = self.positionZEdit.value()
        position = (positionX, positionY, positionZ)

        # Create a command to update the selected entity's position
        command = Command(self.selectedEntity, {'position': position})
        command.execute()

        # Add it to the history
        self.history = self.history[:self.history_index+1]
        self.history.append(command)
        self.history_index += 1

    def applyOrientationChange(self):
        # Get the new orientation
        orientationW = self.orientationWEdit.value()
        orientationX = self.orientationXEdit.value()
        orientationY = self.orientationYEdit.value()
        orientationZ = self.orientationZEdit.value()
        orientation = (orientationW, orientationX, orientationY, orientationZ)

        # Create a command to update the selected entity's orientation
        command = Command(self.selectedEntity, {'orientation': orientation})
        command.execute()

        # Add it to the history
        self.history = self.history[:self.history_index+1]
        self.history.append(command)
        self.history_index += 1

    def applyDimensionChange(self):
        # Get the new dimensions
        dimensionX = self.dimensionXEdit.value()
        dimensionY = self.dimensionYEdit.value()
        dimensionZ = self.dimensionZEdit.value()
        dimensions = (dimensionX, dimensionY, dimensionZ)

        # Create a command to update the selected entity's dimensions
        command = Command(self.selectedEntity, {'dimensions': dimensions})
        command.execute()

        # Add it to the history
        self.history = self.history[:self.history_index+1]
        self.history.append(command)
        self.history_index += 1

    def openColorPicker(self, event):
        color = QColorDialog.getColor(self.selectedEntity.material.diffuse())
        if color.isValid():
            self.updateColorLabel(color)

            # Create a command to update the selected entity's color
            command = Command(self.selectedEntity, {'color': color.getRgb()})
            command.execute()

            # Add it to the history
            self.history = self.history[:self.history_index+1]
            self.history.append(command)
            self.history_index += 1

    def updateColorLabel(self, color):
        palette = self.colorLabel.palette()
        palette.setColor(self.colorLabel.backgroundRole(), color)
        self.colorLabel.setPalette(palette)

    def loadEntity(self, entity):
        self.selectedEntity = entity

        # Update the input fields with the selected entity's attributes
        self.nameEdit.setText(self.selectedEntity.name)

        # Update the color label
        color = self.selectedEntity.material.diffuse()
        self.updateColorLabel(color)

        # Update the position fields
        position = self.selectedEntity.transform.translation()
        print(position.x(), position.y(), position.z())
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

    def undo(self):
        """ There's a bug here where the undo throws an error when the object has already been deleted """
        if self.history_index >= 0:
            self.history[self.history_index].undo()
            self.history_index -= 1

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.history[self.history_index].execute()
