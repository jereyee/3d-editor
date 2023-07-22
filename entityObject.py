from PySide6.QtGui import QQuaternion, QVector3D, QColor
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender

class Entity3D:
    """_summary_

    Attributes:
        entity (Qt3DCore.QEntity): _description_
        mesh (Qt3DExtras.QCuboidMesh): _description_
        name (str): _description_
        material (Qt3DExtras.QDiffuseSpecularMaterial): _description_
        transform (Qt3DCore.QTransform): _description_
        picker (Qt3DRender.QObjectPicker): _description_
        mainWindow (MainWindow): _description_

    Methods:
        to_dict: _description_
        from_dict: _description_
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

    def to_dict(self):
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
        return data

    @staticmethod
    def from_dict(data, root_entity, mainWindow):
        # Create a new entity from a dictionary
        shape_classes = {
            "Cube": Qt3DExtras.QCuboidMesh,
            "Sphere": Qt3DExtras.QSphereMesh
        }
        shape_class = shape_classes.get(data['shape'])
        entity = Entity3D(root_entity, shape_class(), data['name'], mainWindow)
        entity.material.setDiffuse(QColor(*data['color']))
        entity.transform.setTranslation(QVector3D(*data['position']))
        entity.transform.setRotation(QQuaternion(*data['orientation']))
        if data['shape'] == 'Cube':
            entity.mesh.setXExtent(data['dimensions'][0])
            entity.mesh.setYExtent(data['dimensions'][1])
            entity.mesh.setZExtent(data['dimensions'][2])
        elif data['shape'] == 'Sphere':
            entity.mesh.setRadius(data['dimensions'][0])
        return entity