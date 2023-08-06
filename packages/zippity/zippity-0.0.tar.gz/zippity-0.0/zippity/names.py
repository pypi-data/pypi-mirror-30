"""Convenience functions for dealing with objects' fully qualified names."""

# Copyright Aaron Hosford, 2018
# MIT License

import inspect
import sys


def find_object(name: str, *, auto_import: bool = True):
    """Look up an object by fully qualified name, e.g. module.submodule.class.object."""
    if name in sys.modules:
        return sys.modules[name]
    if auto_import:
        try:
            exec('import ' + name)
        except ImportError:
            pass
        else:
            return sys.modules[name]
    if '.' in name:
        pieces = name.split('.')
        child_name = pieces.pop()
        parent_name = '.'.join(pieces)
        parent = find_object(parent_name, auto_import=auto_import)
        return getattr(parent, child_name)
    else:
        raise NameError(name)


def get_fully_qualified_name(named_object) -> str:
    """Get the fully qualified name of an object."""
    if inspect.ismodule(named_object):
        name = named_object.__name__
        if name == '__main__':
            return inspect.getmodulename(named_object.__file__)
        else:
            return name
    else:
        if hasattr(named_object, '__qualname__'):
            name = named_object.__qualname__
        else:
            name = named_object.__name__
        return inspect.getmodule(named_object).__name__ + '.' + name
