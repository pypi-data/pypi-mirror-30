import warnings

from functools import wraps

from astropy.utils.exceptions import AstropyUserWarning

def cached(func):
    """
    Decorator to cache function calls
    """

    @wraps(func)
    def wrapper(self, *args):
        # The cache lives in the instance so that it gets garbage collected
        if (func, args) not in self._cache:
            self._cache[(func, args)] = func(self, *args)
        return self._cache[(func, args)]

    wrapper.wrapped_function = func

    return wrapper

def warn_slow(function):

    @wraps(function)
    def wrapper(self, *args, **kwargs):
        # if the function accepts a 'how', the 'cube' approach requires the whole cube in memory
        warn_how = (kwargs.get('how') == 'cube') or 'how' not in kwargs
        if self._is_huge and not self.allow_huge_operations and warn_how:
            raise ValueError("This function ({0}) requires loading the entire "
                             "cube into memory, and the cube is large ({1} "
                             "pixels), so by default we disable this operation. "
                             "To enable the operation, set "
                             "`cube.allow_huge_operations=True` and try again."
                             .format(str(function), self.size))
        elif warn_how and not self._is_huge:
            # TODO: add check for whether cube has been loaded into memory
            warnings.warn("This function ({0}) requires loading the entire cube into "
                          "memory and may therefore be slow.".format(str(function)))
        return function(self, *args, **kwargs)
    return wrapper

class UnsupportedIterationStrategyWarning(AstropyUserWarning):
    pass

class VarianceWarning(AstropyUserWarning):
    pass

class SliceWarning(AstropyUserWarning):
    pass

class BeamAverageWarning(AstropyUserWarning):
    pass

class WCSCelestialError(Exception):
    pass

class WCSMismatchWarning(AstropyUserWarning):
    pass

class NotImplementedWarning(AstropyUserWarning):
    pass
