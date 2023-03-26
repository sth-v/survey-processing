import abc
import collections

from abc import ABCMeta, abstractmethod

import compas
import randomname
import rpyc
from compas import geometry
import json
import numpy as np
from mmcore.addons import ModuleResolver

from OCC.Core.gp import gp_Pnt
from mmcore.baseitems import Matchable, Entity
from mmcore.baseitems.descriptors import UserDataProperties, JsonView

from jinja2.nativetypes import NativeEnvironment
from mmcore.gql import client as graphql_client
from mmcore.baseitems.descriptors import NoDataDescriptor

with ModuleResolver() as mrslv:
    import rhino3dm


import rhino3dm
import cxm
sess=cxm.S3Session(bucket="box.contextmachine.space")


def is_integer_char(char):
    return str(char) in "0123456789"


class Point(Matchable):
    __match_args__ = "x", "y"
    cxmdata_keys = "X", "Y", "Z"

    def __init__(self, x, y, z=0.0):
        super().__init__(float(x), float(y), z=float(z))

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
                        "normalized": False
                    },
                    "color": {
                        "itemSize": 3,
                        "type": "Float32Array",
                        "array": self.xyz,
                        "normalized": False
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
            "name": self.tag,
            "userData": self.userdata,
            "layers": 1,
            "matrix": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            "geometry": self.geometry()["uuid"],
            "material": "cb806ba5-a7d8-4b02-b578-4fbde75a8fcb"
        }


class NamedPoint(Point):
    __match_args__ = "index", "x", "y", "z", "tag"
    properties = UserDataProperties("index", "tag")
    floor: str = "L2W"

    def __init__(self, index, x, y, z, tag):
        Matchable.__init__(self, int(index), float(x),float(y), float(z), tag.replace("\r", ""))
        self.tag = tag
        self.index = index

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


class SurveyFormat(ES, metaclass=ABCMeta):
    encoding: str = "utf-8"

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

        @abstractmethod
        def parse(self):
            pass

        @property
        def point(self):
            return NamedPoint(*self.data)

        @property
        def point_dict(self):
            dicts = {"index": self.point.index, "x": self.point.x, "y": self.point.y, "z": self.point.z,
                     "tag": self.point.tag}
            print(dicts)
            return dicts

        def commit(self, obj):
            "objects"
            return obj.mutation(variables=self.point_dict)

    @property
    def query(self):
        return graphql_client.GQLReducedQuery(sess.get_object(Key="share/configs/survey/PointsDownloadQuery.graphql")["Body"].read().decode())

    @property
    def mutation(self):
        return graphql_client.GQLReducedQuery(sess.get_object(Key="share/configs/survey/PointsUploadMutation.graphql")["Body"].read().decode())

    def __init__(self, text):

        self.header = []
        self.lines = []
        self.text = text
        self.parse()

        super().__init__(seq=self.lines)

    @classmethod
    def from_file_path(cls, path):
        with open(path, "rb") as fl:
            return cls(fl.read().decode(cls.encoding))

    def commit(self):
        for s in self._seq:
            s.commit(self)

    @abstractmethod
    def parse(self):
        pass

    def colorise(self):
        collections.Counter(self["tag"])

    def dump3dm(self):
        que2 = graphql_client.GQLReducedQuery("""
        query MyQuery {
          lht_triangles_transforms_by_pk(name: "geodesy") {
            value
          }
        }
        """)
        transform_value = que2()["value"]
        model = rhino3dm.File3dm()
        from mmcore.addons.rhino.native import utils
        trx=utils.rhino_transform_from_matrix(np.asarray(transform_value).reshape((4,4)))

        for pt in self["point"]:

            attrs = rhino3dm.ObjectAttributes()
            print(pt)
            attrs.Name = pt.tag


            for k, v in pt.userdata["properties"].items():
                attrs.SetUserString(k, v)
            pt=rhino3dm.Point3d(pt.y, pt.x, pt.z) # It is ok!!!
            pt.Transform( trx)

            model.Objects.Add(rhino3dm.Point(pt), attrs)

        return model

    @property
    def pts(self):
        return list(self["point"])


class SokkiaSDLFormat(SurveyFormat):
    class Line(SurveyFormat.Line):

        def parse(self):
            self.raw_tag = self[4: 20].replace(" ", "")
            self.pref = self[:4]

            self.data = np.asarray(self.parse_line(self[20:].replace("\r", "")), dtype=float).tolist()

        @property
        def point(self):
            return NamedPoint(*self.data, user_tag=self.raw_tag, tag=self.tag, pref=self.pref, index=self.index)

    @classmethod
    def from_file_path(cls, path="/Users/andrewastakhov/Downloads/Telegram Desktop/LAHTA.txt"):
        return super().from_file_path(path)

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


class CxmFormat(SurveyFormat):
    class Line(SurveyFormat.Line):
        @property
        def part(self):
            return randomname.get_name()

        def parse(self):
            splitted = self.replace("\r", "").replace(" ", "").split(",")
            self.data = list(splitted)
            print(self.data)

        @property
        def point(self):
            self.parse()
            return NamedPoint(*self.data)

    def parse(self):
        all_lines = self.text.replace("\r", "").split("\n")
        del all_lines[-1]
        self.lines = []
        for i, ln in enumerate(all_lines):
            self.lines.append(self.Line(ln))

    def categorise(self):
        vals = []
        for k in collections.Counter(ES(self["point"])["tag"]).keys():
            vals.append(self.search_from_key_value("tag", k))
