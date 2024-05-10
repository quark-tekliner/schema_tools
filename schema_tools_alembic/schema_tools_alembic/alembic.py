from collections import defaultdict

import re
from dataclasses import dataclass
from enum import EnumType, Enum
from typing import Type

from schema_tools.decorator_types import FieldDefinition, TypeDefinition


class Deps(set):

    @property
    def python_imports(self):
        by_package = defaultdict(set)
        for d in self:
            if type(d) != tuple:
                continue
            by_package[d[0]].add(d[1] if len(d) < 3 else f'{d[1]} as {d[2]}')
        return sorted([f'from {k} import {", ".join(sorted(v))}' for k, v in by_package.items()])


deps = Deps()


@dataclass(kw_only=True)
class T(TypeDefinition):
    location: str = None
    unique: list[str] = None

    @property
    def table_repr(self):
        p = self.location.split('.')
        if len(p) > 2:
            raise RuntimeError('Invalid `location` attribute')
        return f"__tablename__ = '{p[-1]}'"

    @property
    def unique_repr_as_list(self):
        columns = []
        for t in self._bases_tags + [self]:
            if t.unique is None or len(t.unique) == 0:
                continue
            columns.append([f"'{u}'" for u in t.unique])
        if len(columns) == 0:
            return []
        deps.add(('sqlalchemy', 'UniqueConstraint',))
        return [f'UniqueConstraint({", ".join(c)})' for c in columns]

    @property
    def schema_repr(self):
        p = self.location.split('.')
        if len(p) == 1:
            return
        elif len(p) == 2:
            return f"schema='{p[0]}'"
        else:
            raise RuntimeError('Invalid `location` attribute')

    @property
    def comment_repr(self):
        if len(self._comment) > 0:
            return f'comment="{self._comment}"'

    @property
    def kw_args_repr_as_list(self):
        return [f for f in [self.schema_repr, self.comment_repr] if f is not None]


@dataclass(kw_only=True)
class F(FieldDefinition):
    primary_key: bool = None
    index: bool = None
    default: str | list[str] = None
    fk: str = None

    @property
    def t_repr(self):
        deps.add(('sqlalchemy', 'Column',))
        if isinstance(self.t, EnumType):
            deps.add(('sqlalchemy', 'Enum',))
            deps.add(('enums', self.t.__name__,))
            ret = f'Enum({self.t.__name__})'
        else:
            sa_type = re.search('([^(]+)', self.t).group(1)
            if sa_type == 'JSONB':
                deps.add(('sqlalchemy.dialects.postgresql', sa_type,))
            else:
                deps.add(('sqlalchemy', sa_type,))
            ret = self.t
        if self._multiple:
            ret = f'ARRAY({ret})'
            deps.add(('sqlalchemy.dialects.postgresql', 'ARRAY',))
        return ret

    @property
    def primary_key_repr(self):
        if self.primary_key:
            return 'primary_key=True'

    @property
    def index_repr(self):
        if self.index:
            return 'index=True'

    @property
    def default_repr(self):
        if self.default is not None:
            if type(self.default) == list:
                defaults = []
                for d in self.default:
                    if isinstance(d, Enum):
                        defaults.append(f"{d.value}")
                    else:
                        if str(d).startswith('func.'):
                            deps.add(('sqlalchemy', 'func',))
                            defaults.append(str(d))
                        elif type(d) == str:
                            defaults.append(f"'{d}'")
                        else:
                            defaults.append(str(d))
                return f'server_default="{{{", ".join(defaults)}}}"'
            if self.default.startswith('func.'):
                deps.add(('sqlalchemy', 'func',))
            return f"server_default={self.default}"

    @property
    def fk_repr(self):
        if self.fk is not None:
            if len(self.fk.split('.')) > 3:
                raise RuntimeError(f'Invalid `fk` attribute `{self.fk}`')
            deps.add(('sqlalchemy', 'ForeignKey',))
            return f"ForeignKey('{self.fk}')"

    @property
    def nullable_repr(self):
        if self._nullable:
            return 'nullable=True'

    @property
    def comment_repr(self):

        if len(self._comment) > 0:
            return f'comment="{self._comment}"'

    @property
    def repr_as_list(self):
        return [f for f in [self.t_repr, self.primary_key_repr, self.index_repr,
                            self.default_repr, self.fk_repr, self.nullable_repr,
                            self.comment_repr] if f is not None]
