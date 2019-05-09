#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging

try:
    from maya import cmds
except ImportError:
    pass

log = logging.getLogger('CameraSequencer')


def sequence_images(cameras, start_frame=1001, img_sequence=None):
    """
    Creates an uber camera from input cameras

    :param cameras(models.Camera list): list of camera objects
    :param start_frame(int): Frame to start animation
    :param img_sequence(str): str of image naming with directory

    :raises: None

    :return: filepath to starting image
    :rtype: str
    """
    dir_path = os.path.dirname(img_sequence)
    images = [cam.image_path for cam in cameras]
    print images


def sequence_cameras(cameras, start_frame=1001, img_sequence=None):
    """
    Creates an uber camera from input cameras

    :param cameras(models.Camera list): list of camera objects
    :param start_frame(int): Frame to start animation

    :raises: None

    :return: None
    :rtype: NoneType
    """
    uber_cam = cmds.camera(name="uber_cam")
    uber_cam[0] = cmds.rename(uber_cam[0], "uber_cam")
    uber_cam[1] = cmds.listRelatives(uber_cam[0], children=True)[0]

    imgPlane = cmds.imagePlane(camera=uber_cam[1])
    cmds.imagePlane(imgPlane[1], edit=True, showInAllViews=False)
    imgPlane[0] = cmds.rename(imgPlane[0], "uber_IMGPLNE")
    imgPlane[1] = cmds.listRelatives(imgPlane[0], children=True)[0]

    cmds.setAttr("%s.fit" % imgPlane[1], 4)
    cmds.setAttr("%s.displayOnlyIfCurrent" % imgPlane[1], 1)
    cmds.connectAttr("%s.horizontalFilmAperture" % uber_cam[1],
                     "%s.sizeX" % imgPlane[1])
    cmds.connectAttr("%s.verticalFilmAperture" % uber_cam[1],
                     "%s.sizeY" % imgPlane[1])

    for t, cam in enumerate(cameras):

        frameNumber = (t + start_frame)
        translation = cam.translation
        rotation = cam.rotation

        for i, direction in enumerate(["X", "Y", "Z"]):

            cmds.setKeyframe(uber_cam[0],
                             value=translation[i],
                             attribute="translate%s" % direction,
                             inTangentType="spline",
                             outTangentType="spline",
                             time=frameNumber)

            cmds.setKeyframe(uber_cam[0],
                             value=rotation[i],
                             attribute="rotate%s" % direction,
                             inTangentType="spline",
                             outTangentType="spline",
                             time=frameNumber)

        cmds.setKeyframe(uber_cam[1],
                         value=cam.focal_length,
                         attribute="focalLength",
                         inTangentType="spline",
                         outTangentType="spline",
                         time=frameNumber)

        filmback = cam.filmback

        cmds.setKeyframe(uber_cam[1],
                         value=filmback[0],
                         attribute="horizontalFilmAperture",
                         inTangentType="spline",
                         outTangentType="spline",
                         time=frameNumber)

        cmds.setKeyframe(uber_cam[1],
                         value=filmback[1],
                         attribute="verticalFilmAperture",
                         inTangentType="spline",
                         outTangentType="spline",
                         time=frameNumber)

    cmds.refresh()

    return uber_cam
