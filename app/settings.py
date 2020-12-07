#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from PyQt5 import QtCore


class Settings(QtCore.QSettings):
    """Настройки приложения"""

    def __init__(self, parent=None):
        super().__init__("res/settings.ini", QtCore.QSettings.IniFormat, parent)
        # Инвертировать отмывку
        self.full_screen = self.value('interface/fullscreen', 0)
        print(self.full_screen)

    def write(self):
        """Сохраняет настройки"""
        # Инвертировать отмывку
        self.setValue('interface/fullscreen', self.full_screen)
