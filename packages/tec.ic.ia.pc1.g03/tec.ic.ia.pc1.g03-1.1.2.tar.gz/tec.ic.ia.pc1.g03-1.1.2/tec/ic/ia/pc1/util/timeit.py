# -----------------------------------------------------------------------------

"""
Módulo con la función decoradora para tomar el tiempo que dura cada función
"""

from time import time

# -----------------------------------------------------------------------------


def timeit(method):

    def timed(*args, **kw):
        ts = time()
        result = method(*args, **kw)
        te = time()
        print("Duración de " + method.__name__ + ": "+str(te - ts))
        return result

    return timed

# -----------------------------------------------------------------------------
