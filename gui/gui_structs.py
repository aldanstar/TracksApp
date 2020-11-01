from PySide2.QtCore import Qt, QAbstractTableModel
from PySide2.QtWidgets import QMenuBar

class menu_bar(QMenuBar):
    def __init__(self, parent):
        QMenuBar.__init__(self, parent=None)

    def addItem(self, obj):
        if obj.action():
            action = self.addAction(obj.title, obj.action())
        else:
            item = self.addMenu(obj.title)
            for childItem in obj.children():
                if childItem.action():
                    action = item.addAction(childItem.title, childItem.action())
                else:
                    sub_item = item.addMenu(childItem.title)
                    for sub_childItem in childItem.children():
                        action = sub_item.addAction(sub_childItem.title, sub_childItem.action())

class table_model(QAbstractTableModel):
    def __init__(self, data, header):
        super(table_model, self).__init__()
        self._data = data
        self.header = header

    def setData(self, data):
        self._data = data
        self.beginResetModel()
        self.currentItemIdx = len(self._data)
        self.endResetModel()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

class menu_item:
    def __init__(self, title, action=None):
        self.title=title
        self.__action=action
        self.__children=[]

    def action(self):
        return self.__action

    def addChild(self, obj):
        self.__children.append(obj)

    def addChildren(self, *objs):
        self.__children=objs

    def children(self):
        return self.__children