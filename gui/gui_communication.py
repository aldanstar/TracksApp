from PySide2.QtWidgets import QDialog, QWidget
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout
from PySide2.QtWidgets import QLabel, QPushButton, QComboBox
from PySide2.QtCore import Qt, QObject, SIGNAL

class com_port_dialog(QDialog):
    def __init__(self, parent, com=None):
        QDialog.__init__(self, parent=None)
        self.__parent = parent
        self.setWindowTitle(u'COM port settings')
        self.setMinimumSize(200, 100)
        self.com=com
        self.comports=self.com.comports()
        self.__com_baudrates=(4800, 9600,115200)

        self.gui_init()

    def gui_init(self):
        layout=QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        self.com_select=setitem_wiget(self, u'COM PORT:', self.change_com, self.auto_select)
        if self.comports:
            self.com_select.addItems(self.comports)
        layout.addWidget(self.com_select)

        self.com_baudrate=setitem_wiget(self, u'Baudrate:', self.change_baudrate)
        self.com_baudrate.addItems(self.__com_baudrates)
        layout.addWidget(self.com_baudrate)

        apply = QPushButton(u'Ok')
        apply.setFixedSize(130,30)

        close_proc =  lambda : self.close()
        QObject.connect(apply, SIGNAL("clicked()"), close_proc)
        layout.addWidget(apply)
        layout.setAlignment(apply, Qt.AlignCenter)

    def change_com(self, text):
        self.com.setCurrent(text)

    def change_baudrate(self, text):
        self.com.setBaudrate(int(text))

    def auto_select(self):
        code=('B')
        self.com.search_device(code,self.__com_baudrates, self.search_result)

    def search_result(self, com=None, baudrate=None, success=False):
        self.com_select.setComoboText(com)
        print(com, baudrate, success)

    def check_rule(self, code):
        pass

    def close(self):
        self.done(1)

class setitem_wiget(QWidget):
    def __init__(self, parent, title, callback=None, action=None):
        QWidget.__init__(self, parent=None)
        self.__parent = parent
        self.__title=title
        self.__action=action
        self.__callback=callback

        self.gui_init()

    def gui_init(self):
        layout=QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        label = QLabel()
        label.setText(self.title())
        layout.addWidget(label)

        self.__combo=QComboBox()
        layout.addWidget(self.__combo)
        self.__combo.currentTextChanged.connect(self.__callback)

        if self.action():
            button = QPushButton(u'Auto')
            layout.addWidget(button)
            button.clicked.connect(self.action())

    def setComoboText(self, text):
        self.__combo.setCurrentText(text)

    def addItem(self, text):
        self.__combo.addItem(text)

    def addItems(self, tupl):
        for t in tupl:
            self.__combo.addItem(str(t))

    def action(self):
        return self.__action

    def title(self):
        return self.__title