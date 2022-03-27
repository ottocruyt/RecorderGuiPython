import numpy as np
import cv2
import enlighten

from ..tools import DebugTool

class CameraTool:
    def __init__(self, width, height, angle_hor, angle_vert):
        # calculate helper parameters
        # maxy respresents the normalized distance between the center and outer pixel in y direction
        # miny represents the same value in negative y direction
        self.maxy = np.tan(angle_hor * np.pi / 360.0)
        self.miny = -self.maxy;

        # maxz respresents the normalized distance between the center and outer pixel in z direction
        # minz represents the same value in negative z direction
        self.maxz = np.tan(angle_vert * np.pi / 360.0)
        self.minz = -self.maxz;

        # distz respresents the normalized distance between the outer pixels in z direction
        # minz represents the same value in negative z direction
        self.distz = self.maxz - self.minz;
        self.disty = self.maxy - self.miny;

        # factorz respresents the normalized and averaged dimension of one pixel in z direction
        # factory respresents the normalized and averaged dimension of one pixel in y direction
        self.factor_z = height / self.distz
        self.factor_y = width / self.disty

    # calcultes the pixel indeces of a point defined in 3d coords (x,y,z)
    def getCameraPositionFrom3DCoords(self, x, y, z):
        norm_z = z / x
        norm_y = y / x
        h = (int)((norm_z - self.minz) * self.factor_z)
        w = (int)((norm_y - self.miny) * self.factor_y)
        return h, w

    def drawRoi(self, draw, objdata, color):
        if objdata.expected_object != None:
            self.drawObjectBox(draw, objdata.expected_object, color)

    def drawObjectBox(self, draw, obj, color):
        if obj != None and obj.pos != None:
            pos1h, pos1w = self.getCameraPositionFrom3DCoords( \
                obj.pos.x - obj.dim.x / 2,
                obj.pos.y - obj.dim.y / 2,
                obj.pos.z - obj.dim.z / 2)
            pos2h, pos2w = self.getCameraPositionFrom3DCoords( \
                obj.pos.x - obj.dim.x / 2,
                obj.pos.y + obj.dim.y / 2,
                obj.pos.z + obj.dim.z / 2)

            pos3h, pos3w = self.getCameraPositionFrom3DCoords( \
                obj.pos.x + obj.dim.x / 2,
                obj.pos.y - obj.dim.y / 2,
                obj.pos.z - obj.dim.z / 2)
            pos4h, pos4w = self.getCameraPositionFrom3DCoords( \
                obj.pos.x + obj.dim.x / 2,
                obj.pos.y + obj.dim.y / 2,
                obj.pos.z + obj.dim.z / 2)

            draw.rectangle([(pos1w, pos1h), (pos2w, pos2h)], outline=color)
            draw.rectangle([(pos3w, pos3h), (pos4w, pos4h)], outline=color)
            draw.line([(pos1w, pos1h), (pos3w, pos3h)], fill=color)
            draw.line([(pos1w, pos2h), (pos3w, pos4h)], fill=color)
            draw.line([(pos2w, pos1h), (pos4w, pos3h)], fill=color)
            draw.line([(pos2w, pos2h), (pos4w, pos4h)], fill=color)

    def drawObjectRect(self, draw, obj, color):
        if obj != None and obj.pos != None:
            objh1, objw1 = self.getCameraPositionFrom3DCoords(obj.pos.x - obj.dim.x / 2,
                                                              obj.pos.y - obj.dim.y / 2,
                                                              obj.pos.z - obj.dim.z / 2)
            objh2, objw2 = self.getCameraPositionFrom3DCoords(obj.pos.x - obj.dim.x / 2,
                                                              obj.pos.y + obj.dim.y / 2,
                                                              obj.pos.z + obj.dim.z / 2)
            draw.rectangle([(objw1, objh1), (objw2, objh2)], outline=color)
            draw.text((objw1 + 5, (objh1 + objh2) / 2 - 5), str(obj.object_type), fill=color)
            draw.text((objw1 + 5, (objh1 + objh2) / 2 + 5), "p:%.3f" % obj.prob, fill=color)