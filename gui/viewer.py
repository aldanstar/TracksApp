from PySide2.QtWidgets import QMainWindow, QWidget, QDockWidget
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout
from PySide2.QtCore import Qt, QRectF, QPointF
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView
from PySide2.QtGui import QPixmap, QImage, QPen, QPolygonF, QFont

import numpy as np

class ViewerArea(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent=None)
        self.parent=parent
        self.gui_init()

    def gui_init(self):
        gLayout=QHBoxLayout()
        gMainWindow=QMainWindow()
        gLayout.addWidget(gMainWindow)
        self.setLayout(gLayout)

        dockWidget = QDockWidget(u'Tracks', self)
        dockWidget.setAllowedAreas(Qt.LeftDockWidgetArea |
                           Qt.RightDockWidgetArea)

        self.imgArea = ImageViewer(self.parent)
        gMainWindow.setCentralWidget(self.imgArea)

        dockWidget.setWidget(self.imgArea)
        gMainWindow.addDockWidget(Qt.LeftDockWidgetArea, dockWidget)



    def add_rect(self, x1, x2, y1, y2):
        self.imgArea.scene.addRect(x1, y1, x2-x1, y2-y1, pen=QPen(Qt.red, 3))

    def add_Polygon(self, arr, xoffset=0, yoffset=0):
        polygon = QPolygonF()
        for p in arr:
            x,y=p[0]
            polygon.append(QPointF(x+xoffset,y+yoffset))
        self.imgArea.scene.addPolygon(polygon, pen=QPen(Qt.blue, 3))

    def add_Text(self, text, x, y):
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        text  = self.imgArea.scene.addText(text, font)
        text.setPos(x, y)

    def load_image(self, path):
        self.imgArea.load_image(path)

    def clear(self):
        self.imgArea.clear()

class ImageViewer(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout = QVBoxLayout()
        layout.addWidget(self.view)

        self.img_width = None
        self.img_height = None

        self.setLayout(layout)

    def load_image(self, image_arr):
        self.clear()

        image_path = QImage(image_arr, image_arr.shape[1], image_arr.shape[0], QImage.Format_RGB888)

        pixmap = QPixmap(image_path)
        self.scene.addPixmap(pixmap)

        self.img_width = pixmap.width()
        self.img_height = pixmap.height()

        self.scale_self()

        self.scene.update()

    def scale_self(self):
        if self.img_width is not None:
            self.view.fitInView(QRectF(0, 0, self.img_width, self.img_height), Qt.KeepAspectRatio)
            self.view.scale(self.img_width / self.scene.width(), self.img_height / self.scene.height())

    def clear(self):
        self.scene.clear()