import time

from ..packages.Qt import QtWidgets


def get_maya_window():
    """
    Get Maya MainWindow as a QWidget.

    :raises: ``RuntimeError`` if no maya window not found

    :return: Maya's main window
    :rtype: QtGui.QWidget
    """
    for widget in QtWidgets.QApplication.instance().topLevelWidgets():

        if widget.objectName() == 'MayaWindow':
            return widget

    raise RuntimeError('Could not locate MayaWindow...')


def wait(delay=1):
    """
    Delay python execution for a specified amount of time

    :raises: None

    :return: None
    :rtype: NoneType
    """
    s = time.clock()

    while True:
        if time.clock() - s >= delay:
            return

        QtWidgets.QApplication.instance().processEvents()
