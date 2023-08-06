import json
import sys
from mangrove_surface.logger import log_exception
import posixpath
if sys.version_info[0] >= 3:
    from inspect import signature
else:
    from funcsigs import signature


class MangroveError(Exception):

    def __init__(self, js):
        if "errors" in js.keys():
            err = js["errors"]
        elif "errs" in js.keys():
            err = js["errs"]
        else:
            err = js
        Exception.__init__(
            self, json.dumps(err, indent=2, sort_keys=True)
        )
        self.resource = js


class Api(object):

    resource = None

    @classmethod
    def resource_manager(cls, resp, controller=None, over_list=False):
        cls.errors_manager(resp, over_list=over_list)
        if resp.status_code == 204:
            return
        if over_list:
            return [cls(el, controller=controller) for el in resp.json()]
        else:
            return cls(resp.json(), controller=controller)

    @classmethod
    def errors_manager(cls, resp, over_list=False):
        if resp.ok:
            return

        content_type = resp.headers["Content-Type"].replace(" ", "").lower()
        if content_type != "application/json;charset=utf-8":
            log_exception(resp.raise_for_status)()
        else:
            js = resp.json()
            raise MangroveError(js)

    @classmethod
    def request(
        cls, controller, method, target=None, resource_manager=None,
        over_list=False, check_license=True, **options
    ):
        if not resource_manager:
            def resource_manager(resp):
                return cls.resource_manager(
                    resp, controller=controller, over_list=over_list
                )
        if not target:
            target = cls.resource
        return controller.request(
            method, target=target, resource_manager=resource_manager,
            check_license=check_license, **options
        )

    @classmethod
    def delete(cls, controller, target=None, data=None):
        resource = cls.resource
        if target:
            resource = posixpath.join(resource, target)

        return cls.request(
            controller, "delete", target=resource, data=data
        )

    @classmethod
    def retrieve(cls, controller, target, resource_manager=None):
        if target:
            target = posixpath.join(cls.resource, target)
        return cls.request(
            controller, "get", target=target, resource_manager=resource_manager
        )

    @classmethod
    def retrieve_all(cls, controller, project_id=None, classifier_id=None):
        options = {}
        if project_id:
            options["params"] = {"project_id": project_id}

        if classifier_id:
            options["params"] = {"classifier_id": classifier_id}

        return cls.request(
            controller, "get", target=cls.resource, over_list=True, **options
        )

    def __init__(self, resource, controller=None):
        self.json = resource
        self._controller = controller

    def update(self):
        def up(resp):
            self.errors_manager(resp)
            self.json = resp.json()
            return self
        return self.retrieve(self._controller, self.id(), resource_manager=up)

    def __getattribute__(self, item):
        js = object.__getattribute__(self, "json")
        if item in js.keys():
            def func():
                return js[item]
            return func
        elif item.startswith("is_") and \
                item[3:] in js.keys() and \
                isinstance(js[item[3:]], bool):
            def func():
                return js[item[3:]]
            return func
        return super(Api, self).__getattribute__(item)

    def __str__(self):
        return json.dumps(self.json, indent=2, sort_keys=True)

    def __equal__(self, other):
        return self.__class__ == other.__class__ and self.id() == other.id()

    def is_failed(self):
        if "errs" in self.json.keys() and self.json["errs"]:
            return True
        elif "steps" in self.json.keys():
            steps = self.json["steps"]
            return steps["failed"] != None
        elif "status" in self.json.keys():
            return self.json["status"] == "failed"
        else:
            raise NotImplementedError()

    def is_completed(self):
        if "steps" in self.json.keys():
            steps = self.json["steps"]
            return (not self.is_failed()) and steps["next"] == [] and \
                (steps["missing"] == None or steps["missing"] == []) and \
                steps["current"] == None
        elif "status" in self.json.keys():
            return self.json["status"] == "completed"
        else:
            raise NotImplementedError()

    def is_running(self):
        if "steps" in self.json.keys():
            steps = self.json["steps"]
            return steps["current"] != None
        elif "status" in self.json.keys():
            return self.json["status"] == "running"
        else:
            raise NotImplementedError()

    def is_terminated(self):
        return self.is_completed() or self.is_failed()

    def is_pending(self):
        return not (self.is_terminated() or self.is_running())
