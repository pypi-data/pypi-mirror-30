#!/usr/bin/env python3

class Const():

    class ConstError(TypeError): pass

    def __init__(self, **args):

        for k in args:
            self.__dict__[k] = args[k]

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError('Can\'t re-assign value to constant "%s"' % (name))

        self.__dict__[name] = value

if __name__ == '__main__':

    const = Const(KEY = 'k')
    print(const.KEY)
