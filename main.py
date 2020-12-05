#-------------------------------------------------------------------------------
 #!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
import sys, os
import numpy as np

from PySide2.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QTabWidget, QDockWidget, QWidget,QLabel
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QFileDialog, QTableView, QTreeView
from PySide2.QtWidgets import QAction
from PySide2.QtCore import Qt, QTranslator

from nnets import imgsep, imgsemseg, counter

from app import Project,tools, com_port

from gui.gui_structs import menu_item, table_model, menu_bar
from gui.viewer import ViewerArea
from gui.status import work_indicator
from gui.gui_communication import com_port_dialog
from gui.additional import about_dialog
from gui.tree import ProjectTreeModel, Node

class main_dialog(QMainWindow):
    def __init__(self, app, title):
        QMainWindow.__init__(self, parent=None)
        self.setWindowTitle(title)
        self.setMinimumSize(500, 400)
        self.app = app
        dw=QDesktopWidget()
        self.resize(dw.width()*0.7,dw.height()*0.7)

        # self.showFullScreen()
        self.gui_init()

    def addStatusObj(self, obj):
            self.statusBar().addWidget(obj)

    def addMenuItem(self, obj):
            newItem=self.menuBar().addItem(obj)

    def addMenuItems(self, *objs):
        for obj in objs:
            newItem=self.menuBar().addItem(obj)

    def on_tab_changed(self):
        self.PreparedArea.imgArea.scale_self()
        self.ThroughArea.imgArea.scale_self()
        self.BacklightArea.imgArea.scale_self()

    def gui_init(self):

        menubar=menu_bar(self)
        self.setMenuWidget(menubar)

        self.tabCentralWidget=QTabWidget()
        self.setCentralWidget(self.tabCentralWidget)


        tableDock = QDockWidget('Statistics', self)
        tableDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, tableDock)

        self.table = QTableView()

        self.statisticsWidget = QWidget()
        layout = QVBoxLayout()
        self.statisticsWidget.setLayout(layout)


        data = [
            ['', '', '']
        ]

        header = ['CLUSTER ID', 'TRACKS(p)', 'AREA(%)']

        self.tablemodel = table_model(data, header)
        self.tablemodel.setData(data)
        self.table.setModel(self.tablemodel)
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()

        self.generalWidget = QWidget()
        self.generalWidget.minimumHeight = 50
        generalWidgetlayout=QVBoxLayout()
        generalWidgetlayout.setAlignment(Qt.AlignCenter)
        self.generalWidget.setLayout(generalWidgetlayout)

        self.infolabel = QLabel()
        self.infolabel.setText('''
                        <p align="center">Tracks detection v 0.1<br>
                        <a href='https://kpfu.ru/geo/structure/departments/department-of-geophysics-and-geoinformation'>
                        Department of Geophysics and<br>
                        Geoinformation Technologies</a></p>

                        ''')
        generalWidgetlayout.addWidget(self.infolabel)

        layout.addWidget(self.table)
        layout.addWidget(self.generalWidget)

        tableDock.setWidget(self.statisticsWidget)


        self.PreparedArea=ViewerArea(self)
        self.tabCentralWidget.addTab(self.PreparedArea, self.tr(u'Prepared'))

        self.ThroughArea=ViewerArea(self)
        self.tabCentralWidget.addTab(self.ThroughArea, self.tr(u'Through light'))

        self.BacklightArea=ViewerArea(self)
        self.tabCentralWidget.addTab(self.BacklightArea, self.tr(u'Backlight'))

        self.tabCentralWidget.currentChanged.connect(self.on_tab_changed)

        treeDock = QDockWidget(self.tr(u'Project tree'), self)
        treeDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, treeDock)

        self.project_tree = QTreeView()
        self.project_tree.doubleClicked.connect(self.on_tree_clicked)
        self.root_node = Node(None)
        self.tree_model = ProjectTreeModel()
        self.project_tree.setModel(self.tree_model)
        treeDock.setWidget(self.project_tree)

    def on_tree_clicked(self, index):
        item = self.project_tree.selectedIndexes()[0]
        if self.app.project.current_sample!=item.model().itemFromIndex(index).sample:
            self.app.project.current_sample = item.model().itemFromIndex(index).sample
            self.app.refresh()

class Application:
    def __init__(self):
        self.title=u'Tracks detection'
        self.segmentation = imgsemseg()
        self.separator = imgsep()
        self.counter = counter()

    def run(self):
        self.app = QApplication(sys.argv)
        translator = QTranslator(self.app)
        translator.load('lang/tr_ru', os.path.dirname(__file__))
        self.app.installTranslator(translator)

        self.project = Project('TEMP')

        self.mainDialog=main_dialog(self, self.title)
        self.mainDialog.show()
        file_menu=menu_item(self.app.tr(u'File'))

        pref_menu=menu_item(u'Preferences')
        ref_menu=menu_item(u'Reference')
        gen_menu=menu_item(u'Device')

        gen_menu.addChildren(menu_item(u'COM port', self.showCOMport))

        file_menu.addChildren(menu_item(u'New', self.newProject),
                              menu_item(u'Open'),
                              menu_item(u'Import...', self.openFile),
                              menu_item(u'Save'),
                              menu_item(u'Exit', self.app.exit))

        pref_menu.addChildren(gen_menu, menu_item(u'Settings'))

        ref_menu.addChildren(menu_item(u'Help'),
                             menu_item(u'About', self.showAbout))

        self.mainDialog.addMenuItems(file_menu, pref_menu, ref_menu)

        com_indicator=work_indicator(u'COM PORT')
        self.mainDialog.addStatusObj(com_indicator)

        sys.exit(self.app.exec_())

    def newProject(self):
        self.mainDialog.PreparedArea.clear()
        self.mainDialog.ThroughArea.clear()
        self.mainDialog.BacklightArea.clear()
        self.project = Project('TEMP')


    def draw_tree(self):
        self.mainDialog.tree_model.clear()
        for sample in self.project.samples.get_sorted_by_id():
            self.mainDialog.tree_model.appendRow(Node(sample))

    def openFile(self):
        path_to_file, _ = QFileDialog.getOpenFileName(self.mainDialog, self.app.tr("Load Image"), self.app.tr(u".\example_imgs"), self.app.tr("Images (*.jpg)"))
        # path_to_file, _ = QFileDialog.getOpenFileName(self.mainDialog, self.app.tr("Load Image"), self.app.tr("~/Desktop/"), self.app.tr("Images (*.jpg)"))

        # Определяем тип файла на просвет или на подсветку
        tools.processing(path_to_file, self.project, self.separator, self.segmentation, self.counter)
        self.refresh()

    def refresh(self):
        self.draw_tree()
        self.fill_table()
        self.updete_viewers()

    def fill_table(self):

        sample = self.project.current_sample

        data=[]

        for track in sample.tracks.get_sorted():
            data.append([str(track.id),str(track.count),str(track.area)])

        self.mainDialog.tablemodel.setData(data)
        self.mainDialog.table.resizeRowsToContents()
        self.mainDialog.table.resizeColumnsToContents()

        count = round(np.sum([track.count for track in sample.tracks.get_sorted_by_id()]),2)
        general_area = round(np.sum([track.area for track in sample.tracks.get_sorted_by_id()]),2)

        self.mainDialog.infolabel.setText('''
                        <p align="center">General tracks count<br>{tracks_count}</p>
                        <p align="center">General tracks area (%)<br>{general_area}</p>
                        '''.format(tracks_count=count, general_area=general_area))

    def draw_objects(self, viewer, sample):
        for track in sample.tracks.get_sorted():
            viewer.add_rect(track.left, track.rigth, track.top, track.bottom)
            viewer.add_Polygon(track.contour, track.left, track.top)
            text = 'Count: {tracks_count}\nArea (%): {general_area}'.format(tracks_count=track.count, general_area=track.area)

            viewer.add_Text(text, track.left, track.top)

    def updete_viewers(self):
        sample = self.project.current_sample

        self.mainDialog.ThroughArea.load_image(sample.through)
        self.mainDialog.BacklightArea.load_image(sample.backlight)
        self.mainDialog.PreparedArea.load_image(sample.prepared)

        self.draw_objects(self.mainDialog.ThroughArea, sample)
        self.draw_objects(self.mainDialog.BacklightArea, sample)
        self.draw_objects(self.mainDialog.PreparedArea, sample)


    def showAbout(self):
        about = about_dialog(self)
        about.open()

    def showCOMport(self):
        com=com_port()
        com_dialog = com_port_dialog(self, com)
        com_dialog.open()


def main():
    application=Application()
    application.run()

if __name__ == '__main__':
    main()
