from dataclasses import dataclass
from typing import Type


@dataclass(kw_only=True)
class Definition:

    @property
    def gen(self):
        return self.__class__.__module__.split('.')[-1]


@dataclass(kw_only=True)
class TypeDefinition(Definition):

    _comment = None
    _bases_tags = []

    def set_comment(self, comment):
        self._comment = comment

    def set_bases_tags(self, tags):
        self._bases_tags = tags


@dataclass(kw_only=True)
class FieldDefinition(Definition):
    t: str | Type
    alias: str = None

    _nullable = False
    _multiple = False
    _comment = None
    _name = None

    def make_nullable(self):
        self._nullable = True

    def make_multiple(self):
        self._multiple = True

    def set_comment(self, comment):
        self._comment = comment

    def set_name(self, name):
        self._name = name

    @property
    def name_repr(self):
        if self.alias is not None:
            return self.alias
        if self._name is None:
            raise RuntimeError('Name not set')
        return self._name
