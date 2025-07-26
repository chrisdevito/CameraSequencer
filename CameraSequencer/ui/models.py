import logging

try:
    from maya import cmds, OpenMaya
except ImportError:
    pass

log = logging.getLogger("CameraSequencer")


class Camera(object):
    """
    Maya Camera object.
    """

    def __init__(self, camera="perspShape"):
        if cmds.nodeType(camera) == "transform":
            self.transform = camera
            self.shape = self.getShape(camera)

        elif cmds.nodeType(camera) == "camera":
            self.shape = camera
            self.transform = cmds.listRelatives(camera, parent=True)[0]

        else:
            log.error("%s is not a camera" % camera)
            raise RuntimeError("%s is not a camera" % camera)

    def __repr__(self):
        return "<%s instance of %s>" % (self.__class__.__name__, self.shape)

    def __mobject__(self):
        msel = OpenMaya.MSelectionList()
        msel.add(self.transform, 0)

        mobject = OpenMaya.MObject()
        msel.getDependNode(0, mobject)

        return mobject

    def getShape(self, transform):
        try:
            shape = cmds.listRelatives(transform, children=True, type="camera")[
                0
            ]

            return shape

        except:
            log.error("%s is not a camera" % transform)
            raise RuntimeError("%s is not a camera" % transform)

    @property
    def name(self):
        return self.transform

    @name.setter
    def name(self, value):
        self.transform = value
        self.shape = self.getShape(value)

    @property
    def focal_length(self):
        return cmds.getAttr(self.name + ".focalLength")

    @property
    def filmback(self):
        return [
            cmds.getAttr(self.name + ".horizontalFilmAperture"),
            cmds.getAttr(self.name + ".verticalFilmAperture"),
        ]

    @property
    def translation(self):
        return cmds.xform(
            self.transform, query=True, worldSpace=True, translation=True
        )

    @property
    def rotation(self):
        return cmds.xform(
            self.transform, query=True, worldSpace=True, rotation=True
        )

    @property
    def image_path(self):
        img_planes = cmds.listConnections(self.shape, type="imagePlane")

        if img_planes:
            img_planeshape = cmds.listRelatives(img_planes[0], children=True)[0]

            return cmds.getAttr(img_planeshape + ".imageName")
