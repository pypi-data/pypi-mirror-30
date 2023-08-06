# Zippity

*A simple zip file-based persistence library*

Copyright Aaron Hosford, 2018 (MIT License)


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


To make your class zippable, inherit from `zippity.Zippable` and implement the 
_iter_data and _iter_children methods. The _iter_children method should yield
a tuple `(name, object)` for each member of your class that is itself a 
zippable object. The _iter_data method should yield a tuple `(name, 
loader_func, data)` for each persistent member of your class that is not 
itself a `Zippable` instance. The built-in objects `None`, `bool`, `int`, 
`float`, `str`, and `ast.literal_eval` are supported as loaders. To use your 
own loader, the loader function must be a named method of your class -- not a 
`lambda`, an ordinary function outside of a class, or a method of some 
non-`Zippable` class.
