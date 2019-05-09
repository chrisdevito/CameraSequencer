#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
from .widgets import (CameraList, ObjectItem, LineEditWidget)
from .models import Camera

try:
    from maya import (cmds, OpenMaya)
except ImportError:
    pass

from functools import partial
from collections import defaultdict

try:
    from ..packages.Qt import QtWidgets, QtCore
except ImportError:
    pass

from .. import api

this_package = os.path.abspath(os.path.dirname(__file__))
this_path = partial(os.path.join, this_package)
imgs_path = os.environ.get('M_TASK_PATH', None)

log = logging.getLogger("CameraSequencer")


class UI(QtWidgets.QDialog):
    """
    :class:`UI` inherits a QDialog and customizes it.
    """
    def __init__(self, parent=None):

        super(UI, self).__init__(parent)

        # Set window
        self.setWindowTitle("Camera Sequencer")
        self.resize(450, 275)

        # Grab stylesheet
        with open(this_path("style.css")) as f:
            self.setStyleSheet(f.read())

        # Center to frame.
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Our main layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.maya_hooks = MayaHooks(parent=self)
        self.maya_hooks.before_scene_changed.connect(self.clear_lists)

        self.create_layout()
        self.create_connections()
        self.create_tooltips()

        self.setLayout(self.layout)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def create_layout(self):
        """
        Creates layout.

        :raises: None

        :return: None
        :rtype: NoneType
        """
        self.label = QtWidgets.QLabel("Camera List:")
        self.cam_list = CameraList(self)

        self.up_button = QtWidgets.QPushButton("Move Up")
        self.up_button.setMinimumWidth(100)
        self.up_button.setMinimumHeight(25)

        self.down_button = QtWidgets.QPushButton("Move Down")
        self.down_button.setMinimumWidth(100)
        self.down_button.setMinimumHeight(25)

        self.add_button = QtWidgets.QPushButton("Add")
        self.add_button.setMinimumWidth(100)
        self.add_button.setMinimumHeight(25)

        self.remove_button = QtWidgets.QPushButton("Remove")
        self.remove_button.setMinimumWidth(100)
        self.remove_button.setMinimumHeight(25)

        self.browse_button = QtWidgets.QPushButton("Browse")
        self.browse_button.setMinimumWidth(100)
        self.browse_button.setMinimumHeight(25)

        self.dir_path = LineEditWidget()
        self.dir_path.setMinimumHeight(25)
        self.dir_path.setText("Path to sequence images")

        self.seq_button = QtWidgets.QPushButton("Sequence Camera")
        self.seq_button.setMinimumHeight(40)

        self.start_frame_lbl = QtWidgets.QLabel("Start Frame :")
        self.start_frame_spnbox = QtWidgets.QSpinBox()
        self.start_frame_spnbox.setMinimum(-999999)
        self.start_frame_spnbox.setMaximum(999999)
        self.start_frame_spnbox.setValue(
            int(cmds.playbackOptions(query=True, minTime=True)))
        self.start_frame_spnbox.setAlignment(QtCore.Qt.AlignRight)

        self.start_frame_spnbox.setMinimumWidth(100)
        self.start_spacer = QtWidgets.QSpacerItem(
            100, 25,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)

        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.cam_layout = QtWidgets.QHBoxLayout()
        self.button_layout = QtWidgets.QVBoxLayout()
        self.add_remove_layout = QtWidgets.QVBoxLayout()
        self.file_layout = QtWidgets.QHBoxLayout()
        self.start_frame_layout = QtWidgets.QHBoxLayout()

        self.start_frame_layout.addItem(self.start_spacer)
        self.start_frame_layout.addWidget(self.start_frame_lbl, 0)
        self.start_frame_layout.addWidget(self.start_frame_spnbox, 0)

        self.button_layout.addWidget(self.up_button, 1)
        self.button_layout.addWidget(self.down_button, 1)
        self.button_layout.addWidget(self.add_button, 1)
        self.button_layout.addWidget(self.remove_button, 1)
        self.button_layout.setContentsMargins(5, 0, 0, 0)

        self.file_layout.addWidget(self.dir_path, 1)
        self.file_layout.addWidget(self.browse_button, 0)

        self.cam_layout.addWidget(self.cam_list, 1)
        self.cam_layout.addLayout(self.button_layout)

        self.layout.addWidget(self.label)
        self.layout.addLayout(self.cam_layout)
        self.layout.addLayout(self.start_frame_layout, 1)
        self.layout.addWidget(self.line, 1)
        self.layout.addLayout(self.file_layout)
        self.layout.addWidget(self.seq_button)

    def create_connections(self):
        """
        Creates connections to buttons.

        :raises: None

        :return: None
        :rtype: NoneType
        """
        self.up_button.clicked.connect(self.move_items_up)
        self.down_button.clicked.connect(self.move_items_down)
        self.remove_button.clicked.connect(self.delete_obj_items)
        self.add_button.clicked.connect(self.add_clicked)
        self.seq_button.clicked.connect(self.sequence_camera)
        self.browse_button.clicked.connect(self.browse_dirs)

    def create_tooltips(self):
        """
        Creates tool tips for various widgets.

        :raises: None

        :return: None
        :rtype: NoneType
        """
        self.up_button.setToolTip("Move all selected cameras up by one index.")
        self.down_button.setToolTip("Move all selected cameras"
                                    " down by one index.")
        self.remove_button.setToolTip("Remove all selected"
                                      " cameras from list.")
        self.add_button.setToolTip("Add all selected camera from list.")
        self.seq_button.setToolTip("Create a sequence camera.")
        self.cam_list.setToolTip("Cameras added to the list"
                                 " are in order\n of the camera"
                                 " to be sequenced.")

    def browse_dirs(self):
        """
        Makes the browse window

        :raises: None

        :return: None
        :rtype: NoneType
        """
        if imgs_path:
            start_path = imgs_path + os.sep + "REFERENCE"

        save_path = QtWidgets.QFileDialog.getSaveFileName(
            self,
            'Path to copy images',
            start_path)[0]

        if save_path:
            filename = os.path.basename(save_path).split(".")[0]
            full_path = os.path.dirname(save_path) + os.sep + filename
            self.dir_path.setText(
                full_path + ".<frame>.<ext>")

    def clear_lists(self):
        """
        Clears list

        :raises: None

        :return: None
        :rtype: NoneType
        """
        self.maya_hooks.clear_callbacks()
        self.cam_list.clear()

    def add_clicked(self):
        """
        Add button

        :raises: None

        :return: None
        :rtype: NoneType
        """
        nodes = cmds.ls(selection=True)

        for node in nodes:

            if len(self.cam_list.findItems(node, QtCore.Qt.MatchExactly)):
                log.info("%s already added to the list." % node)
                continue

            self.new_obj_item(Camera(node))

    def new_obj_item(self, node):
        """
        Creates a new obj item

        :raises: None

        :return: None
        :rtype: NoneType
        """
        item = ObjectItem(node)

        self.cam_list.addItem(item)

        # Add delete callbacks
        del_callback = partial(self.delete_obj_item, item)
        ren_callback = partial(self.rename_obj_item, item)

        self.maya_hooks.add_about_to_delete_callback(node, del_callback)
        self.maya_hooks.add_named_changed_callback(node, ren_callback)

    def sequence_camera(self):
        """
        Sequences the camera/images

        :raises: None

        :return: None
        :rtype: NoneType
        """
        camera_nodes = []

        for i in xrange(self.cam_list.count()):
            camera_nodes.append(self.cam_list.item(i).camera)

        if not camera_nodes:
            log.error("No cameras added to sequence list.")
            raise RuntimeError("No cameras added to sequence list.")

        start_img_path = None
        start_frame = self.start_frame_spnbox.value()

        # img_path = self.dir_path.text()

        # if os.path.isdir(os.path.dirname(img_path)):
        #     start_img_path = api.sequence_images(
        #         camera_nodes,
        #         start_frame=start_frame,
        #         img_sequence=img_path)

        api.sequence_cameras(
            camera_nodes,
            start_frame=start_frame,
            img_sequence=start_img_path)

    def delete_obj_item(self, item):
        """
        Deletes selected items

        :raises: None

        :return: None
        :rtype: NoneType
        """
        try:
            self.cam_list.takeItem(self.cam_list.indexFromItem(item).row())
        except RuntimeError as e:
            if "Internal C++ object (ObjectItem) already deleted" in str(e):
                pass
                raise

    def delete_obj_items(self):
        """
        Deletes selected items

        :raises: None

        :return: None
        :rtype: NoneType
        """
        try:
            for item in self.cam_list.selectedItems():
                self.cam_list.takeItem(
                    self.cam_list.indexFromItem(item).row())
        except RuntimeError as e:
            if "Internal C++ object (ObjectItem) already deleted" in str(e):
                pass
                raise

    def rename_obj_item(self, item, old_name, new_name):

        try:
            item.rename(new_name)

        except RuntimeError as e:
            if "Internal C++ object (ObjectItem) already deleted" in str(e):
                pass
                raise

    def move_items_up(self):
        """
        Moves selected items up

        :raises: None

        :return: None
        :rtype: NoneType
        """
        newIndexes = []
        lastIndex = self.cam_list.count() - 1
        indexes = sorted([[self.cam_list.indexFromItem(item).row(), item]
                          for item in self.cam_list.selectedItems()])

        for oldIndex, item in indexes:

            newIndex = oldIndex - 1

            if newIndex < 0:
                newIndex = lastIndex

            newIndexes.append(newIndex)

            if newIndex == self.cam_list.indexFromItem(item).row():
                continue

            self.cam_list.takeItem(oldIndex)
            self.cam_list.insertItem(newIndex, item)

        [self.cam_list.item(ind).setSelected(True) for ind in newIndexes]

    def move_items_down(self):
        """
        Moves selected items down

        :raises: None

        :return: None
        :rtype: NoneType
        """
        newIndexes = []
        lastIndex = self.cam_list.count() - 1
        indexes = sorted(
            [[self.cam_list.indexFromItem(item).row(), item]
             for item in self.cam_list.selectedItems()], reverse=True)

        for oldIndex, item in indexes:

            newIndex = oldIndex + 1

            if newIndex > lastIndex:
                newIndex = 0

            newIndexes.append(newIndex)

            if newIndex == self.cam_list.indexFromItem(item).row():
                continue

            self.cam_list.takeItem(oldIndex)
            self.cam_list.insertItem(newIndex, item)

        [self.cam_list.item(ind).setSelected(True) for ind in newIndexes]

    def closeEvent(self, event):
        self.maya_hooks.clear_callbacks()
        self.maya_hooks.clear_scene_callbacks()
        super(UI, self).closeEvent(event)

    def keyPressEvent(self, event):
        '''
        Override key focus issue.
        '''
        if event.key() in (QtCore.Qt.Key.Key_Shift, QtCore.Qt.Key.Key_Control):
            event.accept()
        else:
            event.ignore()


class MayaHooks(QtCore.QObject):
    '''Manage all Maya Message Callbacks (Hooks)'''

    before_scene_changed = QtCore.Signal()
    scene_changed = QtCore.Signal()
    scene_selection_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(MayaHooks, self).__init__(parent=parent)

        self.callback_ids = defaultdict(list)
        self.scene_callback_ids = []

        before_change_messages = [
            OpenMaya.MSceneMessage.kBeforeOpen,
            OpenMaya.MSceneMessage.kBeforeNew,
            OpenMaya.MSceneMessage.kBeforeRemoveReference,
        ]
        for i, msg in enumerate(before_change_messages):
            callback_id = OpenMaya.MSceneMessage.addCallback(
                msg,
                self.emit_before_scene_changed
            )
            self.scene_callback_ids.append(callback_id)

    def emit_before_scene_changed(self, *args):
        self.before_scene_changed.emit()

    def emit_scene_changed(self, *args):
        self.scene_changed.emit()

    def emit_scene_selection_changed(self, *args):
        self.scene_selection_changed.emit()

    def add_named_changed_callback(self, node, callback):

        mobject = node.__mobject__()

        def maya_callback(mobject, old_name, data):
            new_name = OpenMaya.MFnDependencyNode(mobject).name()
            callback(old_name, new_name)

        callback_id = OpenMaya.MNodeMessage.addNameChangedCallback(
            mobject,
            maya_callback,
        )
        self.callback_ids[node].append(callback_id)

    def add_about_to_delete_callback(self, node, callback):

        mobject = node.__mobject__()

        def maya_callback(depend_node, dg_modifier, data):

            callback_ids = self.callback_ids.pop(node, None)
            if callback_ids:
                for callback_id in callback_ids:
                    OpenMaya.MMessage.removeCallback(callback_id)
            callback()

        callback_id = OpenMaya.MNodeMessage.addNodeAboutToDeleteCallback(
            mobject,
            maya_callback,
        )
        self.callback_ids[node].append(callback_id)

    def clear_callbacks(self):
        for node, callback_ids in self.callback_ids.items():
            for callback_id in callback_ids:
                OpenMaya.MMessage.removeCallback(callback_id)
        self.callback_ids = defaultdict(list)

    def clear_scene_callbacks(self):
        for callback_id in self.scene_callback_ids:
            OpenMaya.MMessage.removeCallback(callback_id)
        self.scene_callback_ids = []
