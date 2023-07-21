from PySide6.QtWidgets import (QColorDialog, QDialog,
                               QFormLayout, QLineEdit,
                               QPushButton, QHBoxLayout)
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtGui import QGuiApplication, QMatrix4x4, QQuaternion, QVector3D, QColor


class EditWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit Object")

        # Create a form for editing the selected object's attributes
        self.editForm = QFormLayout(self)

        # Create input fields for the attributes
        self.nameEdit = QLineEdit()
        self.colorEdit = QColorDialog()
        
        # Remove buttons from the color dialog
        self.colorEdit.setOptions(QColorDialog.NoButtons)

        # Create separate input fields for each component of the position
        self.positionXEdit = QLineEdit()
        self.positionYEdit = QLineEdit()
        self.positionZEdit = QLineEdit()

        # Create a QHBoxLayout for the position fields
        self.positionLayout = QHBoxLayout()
        self.positionLayout.addWidget(self.positionXEdit)
        self.positionLayout.addWidget(self.positionYEdit)
        self.positionLayout.addWidget(self.positionZEdit)

        # Create separate input fields for each component of the orientation
        self.orientationWEdit = QLineEdit()
        self.orientationXEdit = QLineEdit()
        self.orientationYEdit = QLineEdit()
        self.orientationZEdit = QLineEdit()

        # Create a QHBoxLayout for the orientation fields
        self.orientationLayout = QHBoxLayout()
        self.orientationLayout.addWidget(self.orientationWEdit)
        self.orientationLayout.addWidget(self.orientationXEdit)
        self.orientationLayout.addWidget(self.orientationYEdit)
        self.orientationLayout.addWidget(self.orientationZEdit)

        # Create separate input fields for each dimension of the object
        self.dimensionXEdit = QLineEdit()
        self.dimensionYEdit = QLineEdit()
        self.dimensionZEdit = QLineEdit()

        # Create a QHBoxLayout for the dimension fields
        self.dimensionLayout = QHBoxLayout()
        self.dimensionLayout.addWidget(self.dimensionXEdit)
        self.dimensionLayout.addWidget(self.dimensionYEdit)
        self.dimensionLayout.addWidget(self.dimensionZEdit)

        # Add the input fields to the form
        self.editForm.addRow("Name:", self.nameEdit)
        self.editForm.addRow("Color:", self.colorEdit)
        self.editForm.addRow("Position:", self.positionLayout)
        self.editForm.addRow("Orientation:", self.orientationLayout)
        self.editForm.addRow("Dimensions:", self.dimensionLayout)

        # Create a save button
        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.saveChanges)
        self.editForm.addRow(self.saveButton)

    def loadEntity(self, entity):
        self.selectedEntity = entity

        # Update the input fields with the selected entity's attributes
        self.nameEdit.setText(self.selectedEntity.name)
        self.colorEdit.setCurrentColor(self.selectedEntity.material.diffuse())

        # Update the position fields
        position = self.selectedEntity.transform.translation()
        self.positionXEdit.setText(str(position.x()))
        self.positionYEdit.setText(str(position.y()))
        self.positionZEdit.setText(str(position.z()))

        # Update the orientation fields
        orientation = self.selectedEntity.transform.rotation()
        self.orientationWEdit.setText(str(orientation.scalar()))
        self.orientationXEdit.setText(str(orientation.x()))
        self.orientationYEdit.setText(str(orientation.y()))
        self.orientationZEdit.setText(str(orientation.z()))

        # Update the dimension fields
        if isinstance(self.selectedEntity.mesh, Qt3DExtras.QCuboidMesh):
            self.dimensionXEdit.setText(str(self.selectedEntity.mesh.xExtent()))
            self.dimensionYEdit.setText(str(self.selectedEntity.mesh.yExtent()))
            self.dimensionZEdit.setText(str(self.selectedEntity.mesh.zExtent()))
            self.dimensionYEdit.setVisible(True)
            self.dimensionZEdit.setVisible(True)
        elif isinstance(self.selectedEntity.mesh, Qt3DExtras.QSphereMesh):
            self.dimensionXEdit.setText(str(self.selectedEntity.mesh.radius()))
            self.dimensionYEdit.setText("")
            self.dimensionZEdit.setText("")
            self.dimensionYEdit.setVisible(False)
            self.dimensionZEdit.setVisible(False)

    def saveChanges(self):
        # Get the new attributes from the input fields
        name = self.nameEdit.text()
        color = self.colorEdit.currentColor()

        # Get the new position
        positionX = float(self.positionXEdit.text())
        positionY = float(self.positionYEdit.text())
        positionZ = float(self.positionZEdit.text())
        position = QVector3D(positionX, positionY, positionZ)

        # Get the new orientation
        orientationW = float(self.orientationWEdit.text())
        orientationX = float(self.orientationXEdit.text())
        orientationY = float(self.orientationYEdit.text())
        orientationZ = float(self.orientationZEdit.text())
        orientation = QQuaternion(
            orientationW, orientationX, orientationY, orientationZ)

        # Get the new dimensions
        dimensionX = float(self.dimensionXEdit.text())
        dimensionY = float(self.dimensionYEdit.text() or '0')
        dimensionZ = float(self.dimensionZEdit.text() or '0')

        # Update the selected entity's attributes
        self.selectedEntity.name = name
        self.selectedEntity.material.setDiffuse(color)
        self.selectedEntity.transform.setTranslation(position)
        self.selectedEntity.transform.setRotation(orientation)

        # Update the dimensions of the selected entity
        if isinstance(self.selectedEntity.mesh, Qt3DExtras.QCuboidMesh):
            self.selectedEntity.mesh.setXExtent(dimensionX)
            self.selectedEntity.mesh.setYExtent(dimensionY)
            self.selectedEntity.mesh.setZExtent(dimensionZ)
        elif isinstance(self.selectedEntity.mesh, Qt3DExtras.QSphereMesh):
            self.selectedEntity.mesh.setRadius(dimensionX)

        # Update the text of the QListWidgetItem
        self.parent().uiWidget.entityWidgetList.currentItem().setText(name)

        # Close the edit window
        self.close()
