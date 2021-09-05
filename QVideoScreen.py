from PyQt5.QtCore import (pyqtSignal, pyqtSlot, pyqtProperty, QSize)
from PyQt5.QtGui import (QMouseEvent, QWheelEvent)
import pyqtgraph as pg
import numpy as np
from QVideoCamera import QVideoCamera
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class QVideoScreen(pg.GraphicsLayoutWidget):

    mousePress = pyqtSignal(QMouseEvent)
    mouseRelease = pyqtSignal(QMouseEvent)
    mouseMove = pyqtSignal(QMouseEvent)
    mouseWheel = pyqtSignal(QWheelEvent)

    options = dict(enableMenu=False,
                   enableMouse=False,
                   invertY=True,
                   lockAspect=True)

    def __init__(self, *args, camera=None, **kwargs):
        pg.setConfigOptions(imageAxisOrder='row-major')
        super().__init__(*args, **kwargs)
        self.setupUi()
        self.pauseSignals(False)
        self.camera = camera

    def setupUi(self):
        self.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.image = pg.ImageItem()
        self.view = self.addViewBox(**self.options)
        self.view.addItem(self.image)

    @pyqtProperty(QVideoCamera)
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, camera):
        logger.debug(f'Setting camera: {type(camera)}')
        self._camera = camera
        if camera is None:
            return
        self.source = camera
        self.updateShape()

    @pyqtProperty(object)
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        try:
            self._source.newFrame.disconnect(self.updateImage)
            self._source.sizeChanged.disconnect(self.updateShape)
        except AttributeError:
            pass
        self._source = source or self.thread
        self._source.newFrame.connect(self.updateImage)
        self._source.sizeChanged.connect(self.updateShape)

    @pyqtSlot(np.ndarray)
    def updateImage(self, image):
        self.image.setImage(image)

    def sizeHint(self):
        return QSize(self.source.width, self.source.height)

    def minimumSizeHint(self):
        return QSize(self.source.width % 2, self.source.height % 2)

    @pyqtSlot()
    def updateShape(self):
        self.view.setRange(xRange=(0, self.source.width),
                           yRange=(0, self.source.height),
                           padding=0, update=True)
        self.update()

    @pyqtSlot(bool)
    def pauseSignals(self, value):
        self._pause = value

    def mousePressEvent(self, event):
        self.mousePress.emit(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.mouseRelease.emit(event)
        event.accept()

    def mouseMoveEvent(self, event):
        if not self._pause:
            self.mouseMove.emit(event)
        event.accept()

    def wheelEvent(self, event):
        if not self._pause:
            self.mouseWheel.emit(event)
        event.accept()
