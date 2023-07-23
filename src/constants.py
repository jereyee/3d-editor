STL_SCALE = 0.01
PERSPECTIVE_PROJECTION_VALUES = (45.0, 16.0 / 9.0, 0.1, 1000.0)
STL_FILE_PATH = "stl/car.stl"

from enum import Enum

from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender

class ShapeType(Enum):
    CUBE = "Cube"
    SPHERE = "Sphere"
    STL = "STL"

# Mapping of shape names to their corresponding classes
shapeClasses = {
    ShapeType.CUBE: Qt3DExtras.QCuboidMesh,
    ShapeType.SPHERE: Qt3DExtras.QSphereMesh,
    ShapeType.STL: Qt3DRender.QMesh
}