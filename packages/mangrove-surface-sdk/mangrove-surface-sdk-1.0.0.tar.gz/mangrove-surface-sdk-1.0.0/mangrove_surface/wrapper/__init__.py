from mangrove_surface.wrapper.misc import waiter, MangroveResourceDelete
from functools import partial, update_wrapper, wraps
from mangrove_surface.api import MangroveError


class Wrapper(object):

    def __init__(self, api_resource, accessor):
        self.api_resource = api_resource
        self.accessor = accessor
        self._controller = accessor._controller

    def __get__(self, obj, objtype):
        return super(Wrapper, self).__get__(self, obj, objtype)

    def name(self):
        if hasattr(self.api_resource, "name"):
            return self.api_resource.name()
        return super(Wrapper, self).__repr__()

    def __repr__(self):
        s = self.name()
        if self.is_completed():
            pass
        elif self.is_failed():
            s += " (failed)"
        elif self.is_running():
            s += " (running)"
        elif self.is_pending():
            s += " (pending)"
        else:
            s += " (?)"

        return s

    def is_failed(self):
        return self.api_resource.is_failed()

    def is_completed(self):
        return self.api_resource.is_completed()

    def is_running(self):
        return self.api_resource.is_running()

    def is_terminated(self):
        return self.api_resource.is_terminated()

    def is_pending(self):
        return self.api_resource.is_pending()

    def delete(self):
        id = self.api_resource.id()
        self.api_resource.delete(self._controller, target=id)

    def wait_until_terminated(self):
        it = waiter()
        while not self.is_terminated():
            next(it)
            self.update()

        self._extra_init_()

    def _extra_init_(self):
        if self.is_failed():
            raise MangroveError(self.api_resource.json)

    def update(self):
        self.api_resource.update()

    def __equal__(self, other):
        return self.__class__ == other.__class__ and \
            self.api_resource == other.api_resource


def should_be_terminated(meth):
    @wraps(meth)
    def inner(self, *args, **kwargs):
        self.wait_until_terminated()
        return meth(self, *args, **kwargs)
    return inner


def run_once(meth):

    class RunOnce:

        def __init__(self):
            self.runs = set()

        def __call__(self, self_d, *args, **kwargs):
            if self_d in self.runs:
                return
            self.runs.add(self_d)
            return meth(self_d, *args, **kwargs)

    ro = RunOnce()

    @wraps(meth)
    def inner(self, *args, **kwargs):
        return ro(self, *args, **kwargs)

    return inner


class _run_once(object):

    def __init__(self, meth):
        self.meth = meth
        self._instances = {}

    def _call_(self, *args, **kwargs):
        res = self.meth(*args, **kwargs)
        return res

    def _no_call_(self, *args, **kwargs):
        return None

    def __get__(self, instance, owner):
        if not instance in self._instances.keys():
            self._instances[instance] = True
            meth = self._call_
        else:
            meth = self._no_call_
        return partial(meth, instance)
