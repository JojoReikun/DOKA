"""Handle a user function which is defined as directory entry"""

from importlib import import_module

class UserFunc():

    def __init__(self, module_name=None, func_name=None, func_arg=None):

        try:
            self.module = import_module(module_name)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(f'Module {module_name} not found!')
        self.func_name = func_name
        self.func_arg = func_arg

    def __call__(self, func_arg=None):
        func = getattr(self.module, self.func_name)
        if func_arg is None:
            func_arg = self.func_arg
        if func_arg is None:
            retval = func()
        else:
            retval = func(func_arg)
        return retval


if __name__ == "__main__":
    # demo 1: os.getcwd()
    func = UserFunc(module_name='os', func_name='getcwd')
    print( 'Current working dir: ', func() )
    # demo 2: numpy arange(100)
    func = UserFunc('numpy', 'arange', 100)
    print( 'Numpy demo: ', func() )
    print( 'Numpy demo with new arg: ', func(20) )

