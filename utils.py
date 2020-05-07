import pickle
import pathlib
import functools
import sys
from types import ModuleType, FunctionType
from gc import get_referents

# Custom objects know their class.
# Function objects seem to know way too much, including modules.
# Exclude modules as well.
BLACKLIST = type, ModuleType, FunctionType


def getsize(obj):
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError('getsize() does not take argument of type: '+ str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size

def lazy_pickle(string):
    """
    Runs `function_to_decorate` only if the pickle
    file does not exists and does nothing otherwise.
    If it runs, it pickles.
    """

    def actual_decorator(function_to_decorate):

        @functools.wraps(function_to_decorate)
        def wrapper(*args, **kwargs):
        
            file_ = pathlib.Path(string + '.pkl')
            if not file_.exists():
                res = function_to_decorate(*args, **kwargs)

                with open(string + '.pkl', 'wb') as fh:
                    pickle.dump(res, fh)
            else:
                print(string, ' exists already. Aborting')

        return wrapper
    return actual_decorator



if __name__ == '__main__':

    
    @lazy_pickle('hola_function')
    def hola():
        return 'Hola'

    def addition(a, b):
        return [a + b], (b  - a)

    hola()
    hola()
    hola()

    lazy_pickle("Suma 3, 4")(addition)(3, 4)
    lazy_pickle("Suma 3, 4")(addition)(3, 4)
    lazy_pickle("Suma 3, 4")(addition)(3, 4)
    lazy_pickle("Suma 3, 4")(addition)(3, 4)
    lazy_pickle("Suma 2, 5")(addition)(2, 5)
