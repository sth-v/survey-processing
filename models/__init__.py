import abc
import collections
import os
import uuid

import threading
import compas
from compas import geometry
import json
import numpy as np
import rhino3dm
from OCC.Core import gp
from OCC.Core.gp import gp_Pnt
from mmcore.baseitems import Matchable, Entity
from mmcore.baseitems.descriptors import UserData, UserDataProperties, JsonView
import jinja2

from jinja2.nativetypes import NativeEnvironment

class BufferGeometry(Matchable):
    def __set__(self, instance, value):
        ...
    def __get__(self, instance, owner):
        ...

    def to_object3d(self):
        return {
            "uuid": "bf788959-f039-41e1-b48b-0702b822b9bf",
            "type": "Points",
            "name": "2.1",
            "userData": {},
            "layers": 1,
            "matrix": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            "geometry": {},
            "material": "cb806ba5-a7d8-4b02-b578-4fbde75a8fcb"
        }
def is_integer_char(char):
    return char in "0123456789"


class Templateble(Matchable):

    def __init_subclass__(cls, template="", **kwargs):
        cls._jinjaenv = NativeEnvironment()

        cls.template = cls._jinjaenv.from_string(cls.setup_temp(template))

        super().__init_subclass__()

    @classmethod
    @abc.abstractmethod
    def setup_temp(cls, temp) -> str:
        ...


class Point(Matchable):
    __match_args__ = "x", "y"
    cxmdata_keys = "X", "Y", "Z"

    def __init__(self, x, y, z=0.0):
        super().__init__(x, y, z=z)

    @property
    def xyz(self) -> tuple[float, float, float]:
        return self.x, self.y, self.z

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    def distance(self, other):
        return euclidean(np.asarray(self.xyz), np.asarray(other))

    def __array__(self, dtype=float, *args, **kwargs):
        return np.ndarray.__array__(np.asarray([self.x, self.y, self.z], dtype=dtype, *args, **kwargs), dtype)

    def __len__(self):
        return len(self.xyz)

    def to_rhino(self):
        return rhino3dm.Point3d(*self.xyz)

    def to_occ(self):
        return gp_Pnt(*self.xyz)

    def to_compas(self) -> compas.geometry.Point:
        return compas.geometry.Point(*self.xyz)

    def to_dict(self, lower=False) -> dict:
        if lower:
            return self.to_dict_lower()
        else:
            dct = {}
            for k in self.cxmdata_keys:
                dct[k] = getattr(self, k.lower())
            return dct

    def to_dict_lower(self) -> dict:
        dct = {}
        for k in self.cxmdata_keys:
            dct[k.lower()] = getattr(self, k.lower())
        return dct

    @classmethod
    def _validate_dict(cls, dct):
        return all(map(lambda k: (k.upper() in dct.keys()) or (k.lower() in dct.keys()), cls.cxmdata_keys))

    @classmethod
    def from_dict(cls, dct: dict) -> 'Point':
        if cls._validate_dict(dct):
            return cls(*dct.values())
        else:
            raise AttributeError

    @classmethod
    def from_rhino(cls, point: rhino3dm.Point3d) -> 'Point':
        return Point(x=point.X, y=point.Y, z=point.Z)

    @classmethod
    def from_occ(cls, point: gp_Pnt) -> 'Point':
        return cls(*point.XYZ())

    @classmethod
    def from_compas(cls, point: compas.geometry.Point) -> 'Point':
        return cls(point.x, point.y, point.z)

    @classmethod
    def setup_temp(cls, template) -> str:
        with open(template, "r") as fl:
            data = fl.read()
        return data
    @property
    def material(self):
        return
    def geometry(self):
        return {
            "uuid": self.uuid,
            "type": "BufferGeometry",
            "data": {
                "attributes": {
                    "position": {
                        "itemSize": 3,
                        "type": "Float32Array",
                        "array": self.xyz,
                        "normalized": false
                    },
                    "color": {
                        "itemSize": 3,
                        "type": "Float32Array",
                        "array": self.xyz,
                        "normalized": false
                    }
                },
                "boundingSphere": {
                    "center": self.xyz,
                    "radius": 0
                }
            }
        }

    def to_object3d(self):

        return {
            "uuid": "bf788959-f039-41e1-b48b-0702b822b9bf",
            "type": "Points",
            "name": "2.1",
            "userData": {},
            "layers": 1,
            "matrix": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            "geometry": {},
            "material": "cb806ba5-a7d8-4b02-b578-4fbde75a8fcb"
        }


class NamedPoint(Point, Entity):
    __match_args__ = "x", "y", "z"
    json = JsonView("x", "y", "z", "userdata")
    properties = UserDataProperties("tag", "pref", "index", "user_tag")

    def __init__(self, x=None, y=None, z=0, **kwargs):
        super().__init__(x, y, z=z)
        Entity.__init__(self, x, y, z=z, **kwargs)

    @classmethod
    def encode(cls, self):
        return self.ToJSON()

    def ToJSON(self):
        dct = {}
        dct |= self.to_dict_lower()
        dct["userData"] = self.userdata
        return json.dumps(dct)




class GeodesPoint(NamedPoint):
    __match_args__ = "x", "y", "z"


from mmcore.collections.multi_description import ES


class SokkiaSDLFormat(ES):
    encoding: str = "latin-1"

    class Line(str):
        def __new__(cls, *args, **kw):
            inst = str.__new__(cls, *args, **kw)
            inst.parse()
            return inst

        @classmethod
        def parse_line(cls, line):
            word = ""
            words = []
            for char in list(line + " "):
                if char == " ":
                    if not (word == ""):
                        words.append(word)
                    word = ""
                    continue
                else:
                    word += char

            return words

        def parse(self):

            self.raw_tag = self[4: 20].replace(" ", "")
            self.pref = self[:4]

            self.data = np.asarray(self.parse_line(self[20:].replace("\r", "")), dtype=float).tolist()

        @property
        def point(self):
            return NamedPoint(*self.data, user_tag=self.raw_tag, tag=self.tag, pref=self.pref, index=self.index)

    @classmethod
    def from_file_path(cls, path="/Users/andrewastakhov/Downloads/Telegram Desktop/LAHTA.txt"):
        with open(path, "rb") as fl:
            return cls(fl.read().decode(cls.encoding))

    def __init__(self, text):

        self.header = []
        self.lines = []
        self.text = text
        self.parse()

        super().__init__(seq=self.lines)
        self.resolve_index()

    def parse(self):
        all_lines = self.text.replace("\r", "").split("\n")
        del all_lines[-1]
        self.header = []
        self.lines = []

        for i, ln in enumerate(all_lines):

            try:
                if all_lines[-1][:4] == all_lines[i][:4]:
                    self.lines.append(self.Line(ln))

                else:
                    self.header.append(ln)
            except Exception as err:
                if ln == "":
                    pass
                else:
                    print(ln)
                    raise err

    def resolve_index(self):
        index = []
        tag = []
        for i, l in enumerate(self["raw_tag"]):
            j = 1
            ll = list(l)
            tag_ = ""
            index_ = ""
            while True:

                if j <= len(ll):

                    if not is_integer_char(ll[-j]):

                        if not ll[-j] == ".":

                            tag_ = "".join(ll[:-j + 1])
                        else:
                            tag_ = "".join(ll[:-j])
                        break
                    else:
                        index_ += ll[-j]
                        j = j + 1

                else:
                    break
            tag.append(tag_)
            index.append(index_)

        self['tag'] = tag
        self['index'] = index

    def colorise(self):
        collections.Counter(self["tag"])

    @property
    def pts(self):
        return list(self["point"])

    def dump3dm(self):
        collections.Counter(self["tag"])
        pcl = rhino3dm.PointCloud()
        for pt in self.pts:
            attrs = rhino3dm.ObjectAttributes()
            attrs.Name = pt.tag

            for k, v in pt.userdata["properties"].items():
                attrs.SetUserString(k, v)
            rhino3dm.File3dmObject(rhino3dm.Point3d(pt.x, pt.y, pt.z), attrs)
            pcl.Add()
        return pcl
