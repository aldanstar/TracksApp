from PySide2.QtWidgets import QTreeView
from PySide2.QtCore import Qt, QAbstractItemModel, QModelIndex
from app.project import Sample
import os

class ProjectTree(QTreeView):
    def __init__(self, parent, mainnodes):
        QTreeView.__init__(self, parent=None)
        self.mainnodes=mainnodes
        self.setMinimumHeight(100)
        self.main_init()

    def refresh(self):
        self.expandAll()

    def model(self):
        return self._model

    def setMainNodes(self,in_nodes):
        self._model.setMainNodes(in_nodes)

    def main_init(self):
        self._model=ProjectTreeModel(self.mainnodes)
        self.setModel(self._model)
        self.refresh()

class Node(object):
    def __init__(self, in_data):
        self._data = in_data
        if type(in_data) == tuple:
            self._data = list(in_data)
            if len(self._data)==3:
                self._data.insert(2, None)
        if type(in_data) is str or not hasattr(in_data, '__getitem__'):
            self._data = [in_data, None, None, None]
        if isinstance(in_data, Sample):
            self._data = [in_data.name, type(in_data), in_data.id, None, in_data]
        self._columncount = len(self._data)
        self._children = []
        self._parent = None
        self._row = 0
        self._maxchildrenrow = 0


    @property
    def name(self):
        return self._data[0]

    @property
    def type(self):
        return self._data[1]

    @property
    def ID(self):
        return self._data[2]

    @property
    def icon(self):
        return self._data[3]

    @property
    def obj(self):
        return self._data[4]

    def data(self, in_column):
        if in_column >= 0 and in_column < len(self._data):
            return self._data[in_column]

    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def children(self):
        return self._children

    def children_data(self):
        return [child.data(0) for child in self._children]

    def child_by_name(self, name):
        for child in self._children:
            if child.data(0)==name:
                return child
                break

    def child(self, in_row):
        if in_row >= 0 and in_row < self.childCount():
            return self._children[in_row]

    def parent(self):
        return self._parent

    def setParent(self,parent):
        self._parent=parent

    def row(self):
        return self._row

    def setRow(self,row):
        self._row=row

    def removeChild(self, in_child):
        self._children.remove(in_child)

    def clear(self):
        self._children = []

    def addChild(self, in_child):
        in_child.setParent(self)
        in_child.setRow(len(self._children))
        self._children.append(in_child)
        self._columncount = max(in_child.columnCount(), self._columncount)

class ProjectTreeModel(QAbstractItemModel):
    def __init__(self, in_nodes):
        QAbstractItemModel.__init__(self)
        self._root = Node(None)
        self._in_nodes  = in_nodes

        for node in in_nodes:
            self._root.addChild(node)

        self.headers = [self.tr('Project Content')]

    def setMainNodes(self,in_nodes):
        self._root.clear()
        self._in_nodes = in_nodes
        for node in in_nodes:
            self._root.addChild(node)

    def getPersistentIndexList(self):
        return  self.persistentIndexList()

    def flags(self, index):
        return  Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]

    def rowCount(self, in_index):
        if in_index.isValid():
            return in_index.internalPointer().childCount()
        return self._root.childCount()

    def addChild(self, in_node, in_parent):
        if not in_parent or not in_parent.isValid():
            parent = self._root
        else:
            parent = in_parent.internalPointer()
        parent.addChild(in_node)

    def index(self, in_row, in_column, in_parent=None):
        if not in_parent or not in_parent.isValid():
            parent = self._root
        else:
            parent = in_parent.internalPointer()

        if not QAbstractItemModel.hasIndex(self, in_row, in_column, in_parent):
            return QModelIndex()

        child = parent.child(in_row)
        if child:
            return QAbstractItemModel.createIndex(self, in_row, in_column, child)
        else:
            return QModelIndex()

    def parent(self, in_index):
        if in_index.isValid():
            p = in_index.internalPointer().parent()
            if p:
                return QAbstractItemModel.createIndex(self, p.row(),0,p)
        return QModelIndex()

    def itemFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()

    def columnCount(self, in_index):
        if in_index.isValid():
            return in_index.internalPointer().columnCount()
            return self._root.childCount()
        return 1

    def data(self, in_index, role):
        if not in_index.isValid():
            return None
        node = in_index.internalPointer()


        if role == Qt.DisplayRole:
            item = node.data(in_index.column())
            if isinstance(item, str):
                name=os.path.basename(node.data(in_index.column()))
            elif isinstance(item, Sample):
                name = node.data(in_index.column()).name
            return self.tr(name)

        if role == Qt.DecorationRole:
                if node.icon is not None:
                    return node.icon

    ##                if node.data(in_index.column()+1) is None:
    ##                    icon = photoscan.WORKSPACE_16
    ##                else:
    ##                    icon = photoscan.FOLDER_16


        if role==Qt.ToolTipRole:
            if node.data(in_index.column()+1) is None:
                tooltip = str(node.data(in_index.column()))+"   (Нет фотографий)"
            else:
                tooltip = str(node.data(in_index.column()))+"   ("+str(node.data(in_index.column()+1))+" фотографий)"
            return tooltip
        return None