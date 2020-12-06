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

# class Node(object):
#     def __init__(self, obj, parent=None):
#         if isinstance(obj, str) or obj is None:
#             self._name = obj
#         else:
#             self._obj = obj
#             self._name = obj.name
#         self._children = []
#         self._parent = parent
#
#         if parent is not None:
#             parent.addChild(self)
#
#     def addChild(self, child):
#         self._children.append(child)
#         child._parent = self
#
#     def name(self):
#         return self._name
#
#     def child(self, row):
#         return self._children[row]
#
#     def insertChild(self, position, child):
#         if position < 0 or position > len(self._children):
#             return False
#
#         self._children.insert(position, child)
#         child._parent = self
#         return True
#
#     def childCount(self):
#         return len(self._children)
#
#     def parent(self):
#         return self._parent
#
#     def setParent(self, new_parent):
#         self._parent._children.remove(self)
#         self._parent = new_parent
#         new_parent._children.append(self)
#
#     def row(self):
#         if self._parent is not None:
#             return self._parent._children.index(self)
#
#     def removeChild(self, position):
#         if position < 0 or position > len(self._children):
#             return False
#         child = self._children.pop(position)
#         child._parent = None
#         return True
#
#     def __repr__(self):
#         return self._name
#
#
# class ProjectTreeModel(QAbstractItemModel):
#     def __init__(self, root, parent=None):
#         super(ProjectTreeModel, self).__init__(parent)
#         self._rootNode = root
#
#     def setData(self, data):
#         self._rootNode = data
#         self.dataChanged.emit(QModelIndex(0,0) , 10)
#
#     def rowCount(self, parent=QModelIndex()):
#         if not parent.isValid():
#             parentNode = self._rootNode
#         else:
#             parentNode = parent.internalPointer()
#
#         return parentNode.childCount()
#
#     def columnCount(self, parent):
#         return 1
#
#     def data(self, index, role):
#
#         if not index.isValid():
#             return None
#
#         node = index.internalPointer()
#
#         if role == Qt.DisplayRole:
#             if index.column() == 0:
#                 return node.name()
#
#     def index(self, row, column, parent):
#         if not parent.isValid():
#             # parent is not valid when it is the root node, since the "parent"
#             # method returns an empty QModelIndex
#             parentNode = self._rootNode
#         else:
#             parentNode = parent.internalPointer()  # the node
#
#         childItem = parentNode.child(row)
#
#         return self.createIndex(row, column, childItem)
#
#     def parent(self, index):
#         node = index.internalPointer()
#
#         parentNode = node.parent()
#
#         if parentNode == self._rootNode:
#             return QModelIndex()
#
#         return self.createIndex(parentNode.row(), 0, parentNode)
#
#     def flags(self, index):
#
#         # Original, inherited flags:
#         original_flags = super(ProjectTreeModel, self).flags(index)
#
#         return (original_flags | Qt.ItemIsEnabled
#                 | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
#                 | Qt.ItemIsDropEnabled)
#
#     def headerData(self, section, orientation, role):
#         if role == Qt.DisplayRole:
#             if section == 0:
#                 return 'SAMPLE'
#
#     def removeRow(self, row, parent):
#         if not parent.isValid():
#             parentNode = self._rootNode
#         else:
#             parentNode = parent.internalPointer()
#
#         parentNode.removeChild(row)
#         return True


    # def setupModelData(self, lines, parent):
    #     parents = [parent]
    #     indentations = [0]
    #
    #     number = 0
    #
    #     while number < len(lines):
    #         position = 0
    #         while position < len(lines[number]):
    #             if lines[number][position] != " ":
    #                 break
    #             position += 1
    #
    #         lineData = lines[number][position:].strip()
    #
    #         if lineData:
    #             # Read the column data from the rest of the line.
    #             columnData = [s for s in lineData.split('\t') if s]
    #
    #             if position > indentations[-1]:
    #                 # The last child of the current parent is now the new
    #                 # parent unless the current parent has no children.
    #
    #                 if parents[-1].childCount() > 0:
    #                     parents.append(parents[-1].child(parents[-1].childCount() - 1))
    #                     indentations.append(position)
    #
    #             else:
    #                 while position < indentations[-1] and len(parents) > 0:
    #                     parents.pop()
    #                     indentations.pop()
    #
    #             # Append a new item to the current parent's list of children.
    #             parent = parents[-1]
    #             parent.insertChildren(parent.childCount(), 1,
    #                     self.rootItem.columnCount())
    #             for column in range(len(columnData)):
    #                 parent.child(parent.childCount() -1).setData(column, columnData[column])
    #
    #         number += 1


# class Node(object):
#
#     def __init__(self, obj, parent=None):
#         if obj is not None:
#             self._sample = obj
#             self._id = obj.id
#             self._name = obj.name
#         else:
#             self._sample = None
#             self._id = None
#             self._name = 'Samples'
#         self._children = []
#         self._parent = parent
#
#         if parent is not None:
#             parent.addChild(self)
#
#     @property
#     def sampleid(self):
#         return self._id
#
#     @property
#     def sample(self):
#         if self._sample is not None:
#             return self._sample
#
#     def addChild(self, child):
#         self._children.append(child)
#         child._parent = self
#
#     def name(self):
#         return self._name
#
#     def child(self, row):
#         return self._children[row]
#
#     def insertChild(self, position, child):
#         if position < 0 or position > len(self._children):
#             return False
#
#         self._children.insert(position, child)
#         child._parent = self
#         return True
#
#     def childCount(self):
#         return len(self._children)
#
#     def parent(self):
#         return self._parent
#
#     def setParent(self, new_parent):
#         self._parent._children.remove(self)
#         self._parent = new_parent
#         new_parent._children.append(self)
#
#     def row(self):
#         if self._parent is not None:
#             return self._parent._children.index(self)
#
#     def removeChild(self, position):
#         if position < 0 or position > len(self._children):
#             return False
#         child = self._children.pop(position)
#         child._parent = None
#         return True
#
#     def __repr__(self):
#         return self._name
#
# class ProjectTreeModel(QAbstractItemModel):
#     def __init__(self, parent=None):
#         super(ProjectTreeModel, self).__init__(parent)
#         self._rootNode = Node(None)
#
#     def rowCount(self, parent=QModelIndex()):
#         if not parent.isValid():
#             parentNode = self._rootNode
#         else:
#             parentNode = parent.internalPointer()
#
#         return parentNode.childCount()
#
#     def columnCount(self, parent):
#         return 1
#
#     def data(self, index, role):
#         """Return whatever the view should display"""
#
#         if not index.isValid():
#             return None
#
#         node = index.internalPointer()
#
#         if role == Qt.DisplayRole:
#             if index.column() == 0:
#                 return node.name()
#
#     def indexFromItem(self, it):
#         root_index = QModelIndex()
#         if isinstance(it, Node):
#             parents = []
#             while it is not self._rootNode:
#                 parents.append(it)
#                 it = it.parent()
#             root = self._rootNode
#             for parent in reversed(parents):
#                 root = root.find_child_by_name(parent.name())
#                 root_index =self.index(root.row(), 0, root_index)
#         return root_index
#
#     def itemFromIndex(self, index):
#         if index.isValid():
#             return index.internalPointer()
#
#     def appendRow(self, item, parent=None):
#         if parent is None:
#             parent = self._rootNode
#         self.appendRows([item], parent)
#
#     def appendRows(self, items, parent=None):
#         if isinstance(items, list):
#             ix = self.indexFromItem(parent)
#             rows = self.rowCount(ix)
#             self.insertRows(rows, items, parent)
#
#     def insertRows(self, position, items, parent=None):
#         parent_index = self.indexFromItem(parent)
#         self.beginInsertRows(parent_index, position, position + len(items) - 1)
#         if parent is None:
#             parent = self._root_node
#         for item in items:
#             parent.addChild(item)
#         self.endInsertRows()
#
#     def rowCount(self, parent=QModelIndex()):
#         node = parent.internalPointer() if parent.isValid() else self._rootNode
#         return node.childCount()
#
#     def index(self, row, column, parent):
#         if not parent.isValid():
#             parentNode = self._rootNode
#         else:
#             parentNode = parent.internalPointer()  # the node
#
#         childItem = parentNode.child(row)
#
#         return self.createIndex(row, column, childItem)
#
#     def parent(self, index):
#         node = index.internalPointer()
#
#         if not isinstance(node, Node):
#             return
#
#         parentNode = node.parent()
#
#         if parentNode == self._rootNode:
#             return QModelIndex()
#
#         return self.createIndex(parentNode.row(), 0, parentNode)
#
#     def flags(self, index):
#
#         # Original, inherited flags:
#         original_flags = super(ProjectTreeModel, self).flags(index)
#
#         return (original_flags | Qt.ItemIsEnabled
#                 | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
#                 | Qt.ItemIsDropEnabled)
#
#     def headerData(self, section, orientation, role):
#         if role == Qt.DisplayRole:
#             if section == 0:
#                 return 'Samples'
#
#     def clear(self):
#         self._rootNode._children = []
#
#     def removeRow(self, row, parent):
#         if not parent.isValid():
#             parentNode = self._rootNode
#         else:
#             parentNode = parent.internalPointer()
#
#         parentNode.removeChild(row)
#         return True

# class Node(object):
#     def __init__(self, obj, parent=None):
#         self._parent = parent
#         if obj is not None:
#             self._id = obj.id
#             self._name = obj.name
#         self._children = []
#
#     def children(self):
#         return self._children
#
#     def hasChildren(self):
#         return bool(self.children())
#
#     def parent(self):
#         return self._parent
#
#     def name(self):
#         return self._name
#
#     def set_name(self, name):
#         self._name = name
#
#     def type_info(self):
#         return 'NODE'
#
#     def columnCount(self):
#         return 1
#
#     def child_count(self):
#         return len(self._children)
#
#     def add_child(self, child):
#         self._children.append(child)
#         child._parent = self
#
#     def insert_child(self, position, child):
#         if 0 <= position < child_count:
#             self._children.insert(position, child)
#             child._parent = self
#             return True
#         return False
#
#     def remove_child(self, position):
#         if 0 <= position < len(self._children):
#             child = self._children.pop(position)
#             child._parent = None
#             return True
#         return False
#
#     def child(self, row):
#         if 0 <= row < self.child_count():
#             return self._children[row]
#
#     def row(self):
#         if self._parent is not None:
#             return self._parent._children.index(self)
#         return -1
#
#     def find_child_by_name(self, name):
#         for child in self._children:
#             if child.name() == name:
#                 return child
#         return None
#
#     def log(self, tab_level=-1):
#         output = ''
#         tab_level += 1
#
#         for i in range(tab_level):
#             output += '\t'
#
#         output += '|____' + self._name + '\n'
#
#         for child in self._children:
#             output += child.log(tab_level)
#
#         tab_level -= 1
#
#         return output
#
#     def __repr__(self):
#         return self.log()

#
# class TemplateTreeModel(QAbstractItemModel):
#     def __init__(self, parent=None):
#         super(TemplateTreeModel, self).__init__(parent)
#         self._root_node = Node(None)
#
#
#     def headerData(self, section, orientation, role=Qt.DisplayRole):
#         if role == Qt.DisplayRole:
#             if section == 0:
#                 return 'Project'
#             else:
#                 return 'Type'
#
#     def removeData(self, position:int):
#         self.beginRemoveRows(QModelIndex(), position, position)
#         self.data_.remove(position)
#         self.endRemoveRows()
#
#     def clear(self):
#         self.beginResetModel()
#         self.data_.clear()
#         self.endResetModel()
#
#     def index(self, row, column, parent):
#         if not self.hasIndex(row, column, parent):
#             return QModelIndex()
#         node = parent.internalPointer() if parent.isValid() else self._root_node
#         if node.children:
#             return self.createIndex(row, column, node.child(row))
#         else:
#             return QModelIndex()
#
#     def parent(self, child):
#         if not child.isValid():
#             return QModelIndex()
#         node = child.internalPointer()
#         if node.row() >= 0:
#             return self.createIndex(node.row(), 0, node.parent())
#         return QModelIndex()
#
#     def rowCount(self, parent=QModelIndex()):
#         node = parent.internalPointer() if parent.isValid() else self._root_node
#         return node.child_count()
#
#     def columnCount(self, parent=QModelIndex()):
#         return 1
#
#     def hasChildren(self, parent= QModelIndex()):
#         node = parent.internalPointer() if parent.isValid() else self._root_node
#         return node.hasChildren()
#
#     def data(self, index: QModelIndex, role=Qt.DisplayRole):
#         if index.isValid() and role in (Qt.DisplayRole, Qt.EditRole, ):
#             node = index.internalPointer()
#             print(node)
#             return node.name()
#
#     def setData(self, index, value, role=Qt.EditRole):
#         if role in (Qt.EditRole,):
#             node = index.internalPointer()
#             node.set_name(value)
#             self.dataChanged.emit(index, index)
#             return True
#         return False
#
#     def flags(self, index: QModelIndex):
#         return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
#
#     def indexFromItem(self, it):
#         root_index = QModelIndex()
#         if isinstance(it, Node):
#             parents = []
#             while it is not self._root_node:
#                 parents.append(it)
#                 it = it.parent()
#             root = self._root_node
#             for parent in reversed(parents):
#                 root = root.find_child_by_name(parent.name())
#                 root_index =self.index(root.row(), 0, root_index)
#         return root_index
#
#     def item_from_path(self, path, sep):
#         depth = path.split(sep)
#         root = self._root_node
#         for d in depth:
#             root = root.find_child_by_name(d)
#             if root is None: return None
#         return root
#
#     def appendRow(self, item, parent=None):
#         self.appendRows([item], parent)
#
#     def appendRows(self, items, parent=None):
#         if isinstance(items, list):
#             ix = self.indexFromItem(parent)
#             self.insertRows(self.rowCount(ix), items, parent)
#
#     def insertRows(self, position, items, parent=None):
#         parent_index = self.indexFromItem(parent)
#         self.beginInsertRows(parent_index, position, position + len(items) - 1)
#         if parent is None:
#             parent = self._root_node
#         for item in items:
#             parent.add_child(item)
#         self.endInsertRows()