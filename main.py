import sys
from PySide6.QtCore import Property, QObject, QPropertyAnimation, Signal, Qt, QTime
from PySide6.QtGui import QGuiApplication, QMatrix4x4, QQuaternion, QVector3D
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QListWidget, QFrame, QListWidgetItem

class Entity3D:
    def __init__(self, root_entity, mesh, material):
        self.entity = Qt3DCore.QEntity(root_entity)
        self.mesh = mesh

        self.transform = Qt3DCore.QTransform()

        self.entity.addComponent(self.mesh)
        self.entity.addComponent(self.transform)
        self.entity.addComponent(material)

class MainWindow(QMainWindow):
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
        layout = QVBoxLayout(widget)
        layout.addWidget(container, 1)

        # Create a list to keep track of the cubes
        self.entityWidgetList = QListWidget()
        layout.addWidget(self.entityWidgetList)

        # Create a button to add cubes
        self.addCubeButton = QPushButton("Add cube")
        self.addCubeButton.clicked.connect(self.addCube)
        layout.addWidget(self.addCubeButton)

        # Create a button to add spheres
        self.addSphereButton = QPushButton("Add sphere")
        self.addSphereButton.clicked.connect(self.addSphere)
        layout.addWidget(self.addSphereButton)

        # Create a button to delete entities
        self.deleteButton = QPushButton("Delete entity")
        self.deleteButton.clicked.connect(self.deleteEntity)
        layout.addWidget(self.deleteButton)

        # Set the widget as the central widget of the window
        self.setCentralWidget(widget)

        # Create the 3D scene
        self.createScene()

        # Create a list to store the entities
        self.entities = []

    def createScene(self):
        # Root entity
        self.rootEntity = Qt3DCore.QEntity()

        # Material
        self.material = Qt3DExtras.QPhongMaterial(self.rootEntity)
        
        # Camera
        self.view.camera().setPosition(QVector3D(0, 0, 100))
        self.view.camera().setViewCenter(QVector3D(0, 0, 30))

        # For camera controls
        self.camController = Qt3DExtras.QOrbitCameraController(self.rootEntity)
        self.camController.setLinearSpeed(180)
        self.camController.setLookSpeed(50)
        self.camController.setCamera(self.view.camera())
        # self.view.camera().setCameraController(self.camController)

        # Set the root entity of the scene
        self.view.setRootEntity(self.rootEntity)

    def addCube(self):

        # Create a cube entity
        cubeEntity = Entity3D(self.rootEntity, Qt3DExtras.QCuboidMesh(), self.material)
        cubeEntity.mesh.setXExtent(5)
        cubeEntity.mesh.setYExtent(5)
        cubeEntity.mesh.setZExtent(5)

        cubeEntity.transform.setScale3D(QVector3D(1, 1, 1))  # Set scale
        cubeEntity.transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 45))  # Set rotation
        cubeEntity.transform.setTranslation(QVector3D(5 * len(self.entities), 0, 0))  # Set position

        self.entities.append(cubeEntity)

        # Create a QListWidgetItem for the cube
        cubeItem = QListWidgetItem("Cube")
        cubeItem.setData(Qt.UserRole, cubeEntity)

        # Add the item to the list
        self.entityWidgetList.addItem(cubeItem)

    def addSphere(self):
        # Create a sphere entity
        sphereEntity = Entity3D(self.rootEntity, Qt3DExtras.QSphereMesh(), self.material)
        sphereEntity.mesh.setRadius(3)
        sphereEntity.transform.setTranslation(QVector3D(5 * len(self.entities), 0, 0))

        self.entities.append(sphereEntity)

        # Create a QListWidgetItem for the sphere
        sphereItem = QListWidgetItem("Sphere")
        sphereItem.setData(Qt.UserRole, sphereEntity)

        # Add the item to the list
        self.entityWidgetList.addItem(sphereItem)

    def deleteEntity(self):
        # Get the selected item
        selectedItem = self.entityWidgetList.currentItem()

        # Remove the cube from the scene and the list
        if selectedItem is not None:
            # Get the entity from the item's data
            selectedEntity = selectedItem.data(Qt.UserRole)

            # Delete the  entity
            selectedEntity.entity.deleteLater()

            # Remove the item from the list
            row = self.entityWidgetList.row(selectedItem)
            self.entityWidgetList.takeItem(row)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
