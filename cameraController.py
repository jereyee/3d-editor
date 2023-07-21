from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.Qt3DInput import Qt3DInput
from PySide6.QtGui import QVector3D, QQuaternion, QWheelEvent, QKeyEvent
from PySide6.Qt3DExtras import Qt3DExtras

class CameraController(Qt3DCore.QEntity):
    def __init__(self, parent=None, camera=Qt3DRender.QCamera()):
        super().__init__(parent)

        self.camera = Qt3DRender.QCamera(self)
        self.dt = 0.001
        self.linearSpeed = 1
        self.lookSpeed = 500
        self.zoomLimit = 0.16
        self.lastPos = None
        self.pan = 0
        self.tilt = 0

        self.mouseDevice = Qt3DInput.QMouseDevice(self)
        self.mouseHandler = Qt3DInput.QMouseHandler(self)
        self.mouseHandler.setSourceDevice(self.mouseDevice)
        self.mouseHandler.pressed.connect(self.onMousePressed)
        self.mouseHandler.positionChanged.connect(self.onMousePositionChanged)
        self.mouseHandler.wheel.connect(self.onMouseWheel)

        self.keyboardDevice = Qt3DInput.QKeyboardDevice(self)
        self.keyboardHandler = Qt3DInput.QKeyboardHandler(self)
        self.keyboardHandler.setSourceDevice(self.keyboardDevice)
        self.keyboardHandler.pressed.connect(self.onKeyPressed)

        self.panProperty = Qt3DCore.QPropertyAnimation(self)
        self.tiltProperty = Qt3DCore.QPropertyAnimation(self)

        self.setUpCameraController(camera)

    def setUpCameraController(self, camera):
        self.camera.lens().setPerspectiveProjection(45.0, 16 / 9, 0.1, 1000.0)
        self.camera.setViewCenter(QVector3D(0, 0, 0))
        self.camera.setPosition(QVector3D(0, 0, 100))
        self.camera.setUpVector(QVector3D(0, 1, 0))

        self.cameraController = Qt3DExtras.QOrbitCameraController(self)
        self.cameraController.setCamera(camera)

    def onMousePressed(self, event):
        self.lastPos = event.position()

    def onMousePositionChanged(self, event):
        if self.lastPos is None:
            return

        mouse = event.position()
        dt = self.dt
        lookSpeed = self.lookSpeed

        if event.buttons() == Qt3DCore.Qt.MouseButton.LeftButton:
            self.pan = -(mouse.x() - self.lastPos.x()) * dt * lookSpeed
            self.tilt = (mouse.y() - self.lastPos.y()) * dt * lookSpeed
            self.onPanTiltChanged()

        self.lastPos = mouse

    def onPanTiltChanged(self):
        upVect = QVector3D(0, 1, 0)
        self.camera.panAboutViewCenter(self.pan, upVect)
        self.camera.tiltAboutViewCenter(self.tilt)

    def onMouseWheel(self, event: QWheelEvent):
        zoomFactor = event.angleDelta().y() * self.dt * self.linearSpeed
        self.zoom(zoomFactor)

    def onKeyPressed(self, event: QKeyEvent):
        if event.key() == Qt3DCore.Qt.Key.Key_PageUp:
            self.zoom(120 * self.dt * self.linearSpeed)
        elif event.key() == Qt3DCore.Qt.Key.Key_PageDown:
            self.zoom(-120 * self.dt * self.linearSpeed)
        elif event.key() == Qt3DCore.Qt.Key.Key_Up:
            self.upODown(100 * self.dt * self.linearSpeed)
        elif event.key() == Qt3DCore.Qt.Key.Key_Down:
            self.upODown(-100 * self.dt * self.linearSpeed)
        elif event.key() == Qt3DCore.Qt.Key.Key_Left:
            self.leftORight(-100 * self.dt * self.linearSpeed)
        elif event.key() == Qt3DCore.Qt.Key.Key_Right:
            self.leftORight(100 * self.dt * self.linearSpeed)

    def zoom(self, rz):
        if rz > 0 and self.zoomDistance(self.camera.position(), self.camera.viewCenter()) < self.zoomLimit:
            return

        self.camera.translate(QVector3D(0, 0, rz), Qt3DRender.QCamera.DontTranslateViewCenter)

    def zoomDistance(self, posFirst, posSecond):
        return (posSecond - posFirst).length()

    def leftORight(self, rx):
        if rx > 0 and self.zoomDistance(self.camera.position(), self.camera.viewCenter()) < self.zoomLimit:
            return
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))
        self.camera.translate(QVector3D(rx, 0, 0))

    def upODown(self, ry):
        if ry > 0 and self.zoomDistance(self.camera.position(), self.camera.viewCenter()) < self.zoomLimit:
            return
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))
        self.camera.translate(QVector3D(0, ry, 0))