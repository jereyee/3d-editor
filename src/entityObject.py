from PySide6.QtGui import QQuaternion, QVector3D, QColor
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtCore import QUrl, QFileInfo
from src.constants import STL_SCALE, ShapeType, shapeClasses


class Entity3D:
    """
    The Entity3D class represents a 3D entity in the scene.

    Attributes
    ----------
    entity : Qt3DCore.QEntity
        The Qt3D entity that this class wraps.
    mesh : Qt3DExtras.QGeometryRenderer
        The mesh that defines the shape of the entity.
    name : str
        The name of the entity.
    material : Qt3DExtras.QDiffuseSpecularMaterial
        The material of the entity.
    transform : Qt3DCore.QTransform
        The transform of the entity.
    picker : Qt3DRender.QObjectPicker
        The object picker for the entity.
    mainWindow : MainWindow
        The main window of the application.

    Methods
    -------
    onClicked(event):
        Handles the event when the entity is clicked.
    toDict():
        Converts the entity to a dictionary.
    setup(scale, rotation, position):
        Sets up the entity with the given scale, rotation, and position.
    updateProperties(data):
        Updates the properties of the entity from a dictionary.
    updateFromDict(data):
        Updates the properties of the entity from a dictionary.
    fromDict(data, root_entity, mainWindow):
        Creates a new entity from a dictionary.
    """

    def __init__(self, root_entity, mesh, name, mainWindow):
        self.entity = Qt3DCore.QEntity(root_entity)
        self.mesh = mesh
        self.name = name
        self.mainWindow = mainWindow
        self.material = Qt3DExtras.QDiffuseSpecularMaterial()
        self.material.setSpecular(QColor(0, 0, 0))

        self.transform = Qt3DCore.QTransform()

        self.entity.addComponent(self.mesh)
        self.entity.addComponent(self.transform)
        self.entity.addComponent(self.material)

        # Create a QObjectPicker and attach it to the entity
        self.picker = Qt3DRender.QObjectPicker(self.entity)
        self.entity.addComponent(self.picker)

        # Connect the clicked signal to a slot
        self.picker.clicked.connect(self.onClicked)

        # Connect mouse movements to the mainWindow
        self.picker.pressed.connect(self.mainWindow.onMousePressed)
        self.picker.released.connect(self.mainWindow.onMouseReleased)
        self.picker.setDragEnabled(True)
        self.picker.moved.connect(self.mainWindow.onMouseMoved)

    def onClicked(self, event):
        self.mainWindow.onEntityClicked(self)

    def toDict(self):
        # Convert the entity to a dictionary
        data = {
            'name': self.name,
            'color': self.material.diffuse().getRgb(),
            'position': (self.transform.translation().x(),
                         self.transform.translation().y(),
                         self.transform.translation().z()),
            'orientation': (self.transform.rotation().scalar(),
                            self.transform.rotation().x(),
                            self.transform.rotation().y(),
                            self.transform.rotation().z()),
        }
        if isinstance(self.mesh, Qt3DExtras.QCuboidMesh):
            data['dimensions'] = (self.mesh.xExtent(),
                                  self.mesh.yExtent(),
                                  self.mesh.zExtent())
            data['shape'] = 'Cube'
        elif isinstance(self.mesh, Qt3DExtras.QSphereMesh):
            data['dimensions'] = (self.mesh.radius(),)
            data['shape'] = 'Sphere'
        elif isinstance(self.mesh, Qt3DRender.QMesh):
            data['dimensions'] = (self.transform.scale3D().x() * (1/STL_SCALE),
                                  self.transform.scale3D().y() * (1/STL_SCALE),
                                  self.transform.scale3D().z() * (1/STL_SCALE))
            data['shape'] = 'STL'
            # Save the source file of the STL mesh
            data['source'] = self.mesh.source().toLocalFile()
        return data

    def setup(self, scale, rotation, position):
        self.transform.setScale3D(scale)  # Set scale
        self.transform.setRotation(rotation)  # Set rotation
        self.transform.setTranslation(position)  # Set position

    def updateProperties(self, data):
        for key, value in data.items():
            if key == 'name':
                self.name = value
            elif key == 'color':
                self.material.setDiffuse(QColor(*value))
            elif key == 'position':
                self.transform.setTranslation(QVector3D(*value))
            elif key == 'orientation':
                self.transform.setRotation(QQuaternion(*value))
            elif key == 'dimensions':
                if isinstance(self.mesh, Qt3DExtras.QCuboidMesh):
                    self.mesh.setXExtent(value[0])
                    self.mesh.setYExtent(value[1])
                    self.mesh.setZExtent(value[2])
                elif isinstance(self.mesh, Qt3DExtras.QSphereMesh):
                    self.mesh.setRadius(value[0])
                elif isinstance(self.mesh, Qt3DRender.QMesh):
                    scaled_values = [v * STL_SCALE for v in value]
                    self.transform.setScale3D(QVector3D(*scaled_values))

    def updateFromDict(self, data):
        # Update the properties of the entity from a dictionary
        self.updateProperties(data)

    @staticmethod
    def fromDict(data, root_entity, mainWindow):
        # Create a new entity from a dictionary
        shape_class = shapeClasses.get(ShapeType[data['shape'].upper()])
        entity = Entity3D(root_entity, shape_class(), data['name'], mainWindow)
        if data['shape'] == 'STL':
            file_info = QFileInfo(data['source'])
            if file_info.exists():
                # Load the STL file
                entity.mesh.setSource(QUrl.fromLocalFile(data['source']))
            else:
                # Show an error message and skip loading the entity
                print(
                    f"Error: STL file {data['source']} does not exist. Skipping entity {data['name']}.")
                return None
        entity.updateProperties(data)
        return entity
