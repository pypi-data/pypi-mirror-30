from functools import wraps
import pandas as pd


def lazy_property(fn):
    attr_name = '_lazy__' + fn.__name__

    @property
    @wraps(fn)
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property


class StringMixin(object):

    def __repr__(self):
        light_dict = dict(self.__dict__)
        for k, v in self.__dict__.items():
            if isinstance(v, (list, pd.DataFrame, pd.Series)) and len(v) > 10:
                light_dict.pop(k)
        items = ("{}={!r}".format(k, v) for k, v in light_dict.items())
        return "{}({})".format(self.__class__.__name__, ", ".join(items))
