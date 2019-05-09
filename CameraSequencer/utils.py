#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal
import logging

log = logging.getLogger('CameraSequencer')

# This is so you can quit the app with a kill process
signal.signal(signal.SIGINT, signal.SIG_DFL)


def show():
    """
    Shows ui in maya

    :raises: None

    :return: None
    :rtype: NoneType
    """
    from .ui.ui import UI
    from .ui import utils

    cam_win = UI(utils.get_maya_window())
    cam_win.show()
