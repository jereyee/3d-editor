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

    """ def update_properties(self, data):
        self.name = data['name']
        self.material.setDiffuse(QColor(*data['color']))
        self.transform.setTranslation(QVector3D(*data['position']))
        self.transform.setRotation(QQuaternion(*data['orientation']))
        if 'shape' in data:
            if data['shape'] == 'Cube':
                self.mesh.setXExtent(data['dimensions'][0])
                self.mesh.setYExtent(data['dimensions'][1])
                self.mesh.setZExtent(data['dimensions'][2])
            elif data['shape'] == 'Sphere':
                self.mesh.setRadius(data['dimensions'][0]) """
    
    def update_properties(self, data):
        for key, value in data.items():
            if key == 'name':
                self.name = value
            elif key == 'color':
                self.material.setDiffuse(QColor(*value))
            elif key == 'position':
                self.transform.setTranslation(QVector3D(*value))
                print(self.transform.translation())
            elif key == 'orientation':
                self.transform.setRotation(QQuaternion(*value))
            elif key == 'dimensions':
                if isinstance(self.mesh, Qt3DExtras.QCuboidMesh):
                    self.mesh.setXExtent(value[0])
                    self.mesh.setYExtent(value[1])
                    self.mesh.setZExtent(value[2])
                elif isinstance(self.mesh, Qt3DExtras.QSphereMesh):
                    self.mesh.setRadius(value[0])

    def update_from_dict(self, data):
        # Update the properties of the entity from a dictionary
        self.update_properties(data)

    @staticmethod
    def from_dict(data, root_entity, mainWindow):
        # Create a new entity from a dictionary
        shape_classes = {
            "Cube": Qt3DExtras.QCuboidMesh,
            "Sphere": Qt3DExtras.QSphereMesh
        }
        shape_class = shape_classes.get(data['shape'])
        entity = Entity3D(root_entity, shape_class(), data['name'], mainWindow)
        entity.update_properties(data)
        return entity