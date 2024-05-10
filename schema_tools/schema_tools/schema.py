import pkgutil
import importlib
import inspect
from enum import Enum


def init(schema_path, schema_name):
    enums = []
    klasses = []
    for loader, name, is_pkg in pkgutil.walk_packages(schema_path, schema_name + '.'):
        module = importlib.import_module(name)
        for enum_name, enum in inspect.getmembers(
                module,
                lambda m: inspect.isclass(m) and issubclass(m, Enum) and m.__name__ != 'Enum'):
            enums.append((f'{name}.{enum_name}', enum,))
        for klass_name, klass in inspect.getmembers(
                module,
                lambda m: inspect.isclass(m) and hasattr(m, '_tags')):
            klasses.append((f'{name}.{klass_name}', klass,))
    return enums, klasses
