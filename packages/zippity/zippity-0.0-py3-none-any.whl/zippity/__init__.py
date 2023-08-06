"""
# Zippity

*A simple zip file-based persistence library*

Usage:

    from zippity import Zippable

    class MyZippableClass(Zippable):

        def __init__(self, members):
            self.simple_member1 = members['simple_member1']
            self.simple_member2 = members['simple_member2']
            self.zippable_member1 = members['zippable_member1']
            self.zippable_member2 = members['zippable_member2']

        def _iter_data(self):
            yield 'simple_member1', int, self.simple_member1
            yield 'simple_member2', str, self.simple_member2

        def _iter_children(self):
            yield 'zippable_member1', self.zippable_member1
            yield 'zippable_member2', self.zippable_member2

    my_zippable_object = MyZippableClass()
    my_zippable_object.save('path/object.zip')

    mzo_copy = MyZippableClass.load('path/object.zip')
"""

# Copyright Aaron Hosford, 2018
# MIT License


import ast
import os
import shutil
import tempfile
import zipfile
from abc import ABCMeta
from typing import Any, Iterator, Tuple, Callable

from zippity.names import find_object, get_fully_qualified_name


def _path_append(parent, child):
    """Utility function for joining paths, ensuring that forward slashes are always used regardless of OS."""
    parent = parent.rstrip('/')
    child = child.lstrip('/')
    return parent + '/' + child


class Zippable(metaclass=ABCMeta):
    """
    Base class for zippable objects. To make your class zippable, inherit from this class and implement the _iter_data
    and _iter_children methods. The _iter_children method should yield a tuple (name, object) for each member of your
    class that is itself a zippable object. The _iter_data method should yield a tuple (name, loader_func, data) for
    each persistent member of your class that is not itself a zippable object. The built-in objects None, bool, int,
    float, str, and ast.literal_eval are supported as loaders. Otherwise, the loader function must be a named method of
    your class -- not a lambda, an ordinary function outside of a class, or a method of some non-Zippable class."""

    @classmethod
    def load(cls, path: str, *, auto_import: bool = True) -> 'Zippable':
        """Load a Zippable instance from a file."""
        with zipfile.ZipFile(path, mode='r') as archive:
            all_paths = {_path_append('/', name): name for name in archive.namelist()}
            object_paths = {os.path.dirname(object_path) for object_path in all_paths
                            if object_path.endswith('/@loader')}
            path_map = {}
            for object_path in sorted(object_paths, key=len, reverse=True):  # type: str
                if os.path.dirname(object_path) not in object_paths:
                    raise ValueError("Parent not found for object at %r" % object_path)
                if object_path != '/' and not all(element.isidentifier() for element in object_path.split('/')[1:]):
                    raise ValueError("Invalid object path: %r" % object_path)

                loader_path = _path_append(object_path, '@loader')
                assert loader_path in all_paths
                loader_name = archive.read(all_paths[loader_path]).decode()
                if not all(element.isidentifier() for element in loader_name.split('.')):
                    raise ValueError("Invalid loader name for object at %r: %r" % (object_path, loader_name))
                loader = find_object(loader_name, auto_import=auto_import)
                if not (loader in (None, bool, int, float, str, ast.literal_eval) or
                        (isinstance(loader, type) and issubclass(loader, Zippable))):
                    loader_class_name = '.'.join(loader_name.split('.')[:-1])
                    if loader_class_name:
                        loader_class = find_object(loader_class_name, auto_import=auto_import)
                    else:
                        loader_class = None
                    if not (isinstance(loader_class, type) and issubclass(loader_class, Zippable)):
                        # Basic security check:
                        raise ValueError("Loader must be None, bool, int, float, str, ast.literal_eval, a Zippable"
                                         "subclass, or a method of a Zippable subclass: %r", loader_name)
                if not callable(loader) or loader in (eval, exec, compile):  # Double-check
                    raise TypeError("Invalid loader for object at %r: %r" % (object_path, loader_name))

                data_path = _path_append(object_path, '@data')
                if data_path in all_paths:
                    data = archive.read(all_paths[data_path])
                else:
                    data = None

                child_map = {os.path.basename(child_path): value
                             for child_path, value in path_map.items()
                             if os.path.dirname(child_path) == object_path}

                if loader in (bool, int, float, str, ast.literal_eval):
                    if child_map:
                        raise ValueError("Literal type with children: %r" % object_path)
                    if loader is str:
                        path_map[object_path] = data.decode()
                    else:
                        path_map[object_path] = loader(data)
                elif loader is None:
                    if child_map:
                        raise ValueError("Literal type with children: %r" % object_path)
                    if data:
                        raise ValueError("None loader cannot accept initialization data.")
                    path_map[object_path] = None
                else:
                    if data is None:
                        try:
                            obj = loader(**child_map)
                        except TypeError:
                            obj = loader(child_map, data)
                    elif not child_map:
                        try:
                            obj = loader(data)
                        except TypeError:
                            obj = loader(child_map, data)
                    else:
                        obj = loader(child_map, data)
                    path_map[object_path] = obj
                    for child_name in child_map:
                        del path_map[_path_append(object_path, child_name)]

        assert len(path_map) == 1 and '/' in path_map
        return path_map.pop('/')

    # noinspection PyMethodMayBeStatic
    def _iter_data(self) -> Iterator[Tuple[str, Callable[[bytes], Any], Any]]:
        """Return an iterator over each data value that should be written to file. For each value, a tuple of the form
        (name, loader_function, object) should be yielded. Override this method in your derived class to save a data
        point."""
        yield from ()

    # noinspection PyMethodMayBeStatic
    def _iter_children(self) -> Iterator[Tuple[str, 'Zippable']]:
        """Return an iterator over each Zippable child object that should be written to file. For each child, a tuple
        of the form (name, object) should be yielded. Override this method in your derived class to save a child object.
        """
        yield from ()

    def _iter_all_elements(self, root: str) -> Iterator[Tuple[str, Callable[[bytes], Any], Any]]:
        """Iterate over all data and Zippable child elements in the object's hierarchy."""
        yield root, type(self), None
        yield from self._iter_data()
        for name, child in self._iter_children():
            yield from child._iter_all_elements(_path_append(root, name))

    def save(self, path: str) -> None:
        """Save the Zippable instance to a file."""
        fd, temp_path = tempfile.mkstemp()
        try:
            # Use a temporary file so we never get partial save results
            with zipfile.ZipFile(temp_path, mode='w', compression=zipfile.ZIP_DEFLATED) as archive:
                for object_path, loader, data in self._iter_all_elements('/'):
                    # TODO: Check the object path, loader, and data ahead of time to avoid delayed errors at load time.
                    if data is not None:
                        if not isinstance(data, (str, bytes)):
                            data = str(data)
                        archive.writestr(_path_append(object_path, '@data'), data)
                    loader_name = get_fully_qualified_name(loader)
                    assert find_object(loader_name) is loader, loader_name
                    archive.writestr(_path_append(object_path, '@loader'), loader_name)
            if os.path.isfile(path):
                if os.path.isfile(path + '.bak'):
                    os.remove(path + '.bak')
                shutil.move(path, path + '.bak')
            shutil.move(temp_path, path)
        finally:
            if os.path.isfile(temp_path):
                os.remove(temp_path)
            os.close(fd)
