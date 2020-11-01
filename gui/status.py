from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel

from res import resources

class work_indicator(QWidget):
    def __init__(self, title):
        QWidget.__init__(self, parent=None)
        self.__title=title
        self.__title_sufix=""
        self.__status=0
        self.__conected_indicator=QPixmap(resources.GREEN_INDICATOR)
        self.__ready_indicator=QPixmap(resources.YELLOW_INDICATOR)
        self.__disconected_indicator=QPixmap(resources.RED_INDICATOR)
        self.__current_indicator=self.__disconected_indicator
        self.gui_init()

    def status(self):
        return self.__status

    def setStatus(self, value):
        self.__status=value

    def update(self):
        self.__current_indicator = self.__current_indicator.scaled(16, 16, Qt.KeepAspectRatio)
        self.indicator.setPixmap(self.__current_indicator)

    def title(self):
        return self.__title

    def sufix(self):
        return self.__title_sufix

    def gui_init(self):
        layout=QHBoxLayout()
        layout.setAlignment(Qt.AlignRight)
        self.setLayout(layout)

        label = QLabel(self)
        label.setText(u'{0}: {1}'.format(self.title(), self.sufix()))
        layout.addWidget(label)

        self.indicator= QLabel(self)
        layout.addWidget(self.indicator)
        self.update()