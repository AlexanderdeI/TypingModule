import os

from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QCursor, QPixmap, QTransform
from PyQt5.QtWidgets import QDesktopWidget, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView

from .settings import *


class PhotoViewer(QGraphicsView):

    leftMouseButtonPressed = pyqtSignal(float, float)
    leftMouseButtonReleased = pyqtSignal(float, float)

    def __init__(self):
        QGraphicsView.__init__(self)
        self.screen = QDesktopWidget().screenGeometry()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.photo_base_dir = None
        self.pixmap_photo = QPixmap()
        self.current_photo = None
        self.zoom = BASE_ZOOM
        self.max_zoom = MAX_PHOTO_ZOOM
        self.min_zoom = MIN_ZOOM
        self.zoom_ratio = ZOOM_RATIO
        self.photo_rotate = 0

        self.ratio_mode = Qt.KeepAspectRatio
        self.setMouseTracking(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFixedSize(self.get_sizes())
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setCursor(QCursor(Qt.OpenHandCursor))

    def get_sizes(self):
        """
        Returns max photo viewer size for typing module window
        :return: QSize
        """
        width = int(self.screen.width() * 0.5)
        height = int(self.screen.height() * 0.875)
        return QSize(width, height)

    def open_photo(self, filename):
        self.current_photo = filename
        path = os.path.join(self.photo_base_dir, filename)
        project_path = os.path.join(PROJECT_PATH, filename)
        self.scene.clear()
        if os.path.isfile(path):
            self._prepare_photo(path)
        elif os.path.isfile(project_path):
            self._prepare_photo(project_path)
        else:
            self.scene.addSimpleText(
                "Отсутствует фотография по указаному пути:\n\n{path}".format(path=path)
            )

    def _prepare_photo(self, path):
        self.pixmap_photo.load(path)
        self.scene.addItem(QGraphicsPixmapItem(self.pixmap_photo))
        self.auto_rotate_photo()
        self.setTransform(QTransform().rotate(self.photo_rotate))
        self.scene.update()
        self.fitInView(self.scene.sceneRect(), mode=self.ratio_mode)

    def auto_rotate_photo(self):
        width = self.pixmap_photo.width()
        height = self.pixmap_photo.height()
        if width > height:
            self.photo_rotate = 90
        else:
            self.photo_rotate = 0

    def zoom_in(self):
        self.zoom *= self.zoom_ratio
        if self.zoom > self.max_zoom:
            self.zoom = self.max_zoom
        self.setTransform(QTransform().scale(self.zoom, self.zoom).rotate(self.photo_rotate))

    def zoom_out(self):
        self.zoom /= self.zoom_ratio
        self.scene.setMinimumRenderSize(1)
        if self.zoom < self.min_zoom:
            self.zoom = self.min_zoom
        self.setTransform(QTransform().scale(self.zoom, self.zoom).rotate((self.photo_rotate)))

    def wheelEvent(self, wheel_event):
        moose = wheel_event.angleDelta().y() / 15 / 8
        if moose > 0:
            self.zoom_in()
        elif moose < 0:
            self.zoom_out()
        # TODO: исправить зум

    def mousePressEvent(self, event):
        pos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.leftMouseButtonPressed.emit(pos.x(), pos.y())
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        QGraphicsView.mouseReleaseEvent(self, event)
        pos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
        self.leftMouseButtonPressed.emit(pos.x(), pos.y())
