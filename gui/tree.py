from PySide2.QtCore import Qt, QAbstractItemModel, QModelIndex

class Node(object):
    def __init__(self, obj, parent=None):
        if obj is not None:
            self._id = obj.id
            self._name = obj.name
        else:
            self._id = None
            self._name = 'Samples'
        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)

    def addChild(self, child):
        self._children.append(child)
        child._parent = self

    def name(self):
        return self._name

    def child(self, row):
        return self._children[row]

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def setParent(self, new_parent):
        self._parent._children.remove(self)
        self._parent = new_parent
        new_parent._children.append(self)

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def removeChild(self, position):
        if position < 0 or position > len(self._children):
            return False
        child = self._children.pop(position)
        child._parent = None
        return True

    def __repr__(self):
        return self._name

class TreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self._rootNode = Node(None)

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        """Return whatever the view should display"""

        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return node.name()

    def indexFromItem(self, it):
        root_index = QModelIndex()
        if isinstance(it, Node):
            parents = []
            while it is not self._rootNode:
                parents.append(it)
                it = it.parent()
            root = self._rootNode
            for parent in reversed(parents):
                root = root.find_child_by_name(parent.name())
                root_index =self.index(root.row(), 0, root_index)
        return root_index

    def appendRow(self, item, parent=None):
        if parent is None:
            parent = self._rootNode
        self.appendRows([item], parent)

    def appendRows(self, items, parent=None):
        if isinstance(items, list):
            ix = self.indexFromItem(parent)
            rows = self.rowCount(ix)
            self.insertRows(rows, items, parent)

    def insertRows(self, position, items, parent=None):
        parent_index = self.indexFromItem(parent)
        self.beginInsertRows(parent_index, position, position + len(items) - 1)
        if parent is None:
            parent = self._root_node
        for item in items:
            parent.addChild(item)
        self.endInsertRows()

    def rowCount(self, parent=QModelIndex()):
        node = parent.internalPointer() if parent.isValid() else self._rootNode
        return node.childCount()

    def index(self, row, column, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()  # the node

        childItem = parentNode.child(row)

        return self.createIndex(row, column, childItem)

    def parent(self, index):
        node = index.internalPointer()

        parentNode = node.parent()

        if parentNode == self._rootNode:
            return QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def flags(self, index):

        # Original, inherited flags:
        original_flags = super(TreeModel, self).flags(index)

        return (original_flags | Qt.ItemIsEnabled
                | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
                | Qt.ItemIsDropEnabled)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if section == 0:
                return 'Samples'

    def clear(self):
        self._rootNode._children = []

    def removeRow(self, row, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        parentNode.removeChild(row)
        return True

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