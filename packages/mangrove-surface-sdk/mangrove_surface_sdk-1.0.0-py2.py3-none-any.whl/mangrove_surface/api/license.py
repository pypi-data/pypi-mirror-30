import json
from mangrove_surface.api import Api


class License(Api):

    resource = "licenses"

    @classmethod
    def retrieve(cls, controller):
        return cls.request(controller, "get")

    @classmethod
    def retrieve_with_request_code(cls, controller):
        return cls.request(
            controller, "get", params="request_code"
        )

    @classmethod
    def new_license(cls, controller, license_code):
        return cls.request(
            controller, "post", params="request_code", data={
                "key": license_code
            }, check_license=False
        )

    __getattribute__ = object.__getattribute__

    def __repr__(self):
        return json.dumps(self.json, indent=2, sort_keys=True)
