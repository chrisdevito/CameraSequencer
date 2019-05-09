#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from ..packages.Qt import QtWidgets, QtGui, QtCore
except ImportError:
    raise

import logging

log = logging.getLogger("CameraSequencer")


class ObjectItem(QtWidgets.QListWidgetItem):

    def __init__(self, camera, *args, **kwargs):
        super(ObjectItem, self).__init__(*args, **kwargs)
        self.setText(camera.name)
        self.camera = camera

    def rename(self, new_name):
        self.camera.name = new_name
        self.setText(self.camera.name)


class CameraList(QtWidgets.QListWidget):
    """
    :class:`CameraListWidget` inherits and creates a custom QListWidget class.
    """
    def __init__(self, *args, **kwargs):

        super(CameraList, self).__init__(*args, **kwargs)

        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setDropIndicatorShown(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setObjectName('cameralist')


class LineEditWidget(QtWidgets.QLineEdit):
    '''
    :class:`LineWidget` deals with building a QLineEdit.

    :raises: None

    :return: None
    :rtype: NoneType
    '''
    def __init__(self, *args, **kwargs):
        super(LineEditWidget, self).__init__(*args, **kwargs)


class LabelWidget(QtWidgets.QLabel):
    '''
    :class:`LabelWidget` deals with building a QLabel.

    :raises: None

    :return: None
    :rtype: NoneType
    '''
    def __init__(self, name, parent=None):

        super(LabelWidget, self).__init__(parent)

        self.setText(name)
        self.setObjectName("{0}_lbl".format(name))

        # Size.
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        self.setSizePolicy(sizePolicy)

        # Font.
        font = QtGui.QFont()
        font.setPointSize(10)
        self.setFont(font)
