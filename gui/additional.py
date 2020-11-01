from PySide2.QtWidgets import QDialog
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QLabel, QPushButton
from PySide2.QtCore import Qt, QObject, SIGNAL

class about_dialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent=None)
        self.setWindowTitle(u'About')
        self.setMinimumSize(200, 100)


        self.gui_init()

    def gui_init(self):
        layout=QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        label = QLabel()
        label.setText('''
                        <p align="center">Tracks detection v 0.1<br>
                        <a href='https://kpfu.ru/geo/structure/departments/department-of-geophysics-and-geoinformation'>
                        Department of Geophysics and<br>
                        Geoinformation Technologies</a></p>

                        ''')
        layout.addWidget(label)

        apply = QPushButton(u'Ok')
        apply.setFixedSize(130,30)

        close_proc =  lambda : self.close()
        QObject.connect(apply, SIGNAL("clicked()"), close_proc)

        layout.addWidget(apply)
        layout.setAlignment(apply, Qt.AlignCenter)

    def close(self):
        self.done(1)