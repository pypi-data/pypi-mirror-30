import json
import os
import posixpath
import requests
from datetime import datetime
from mangrove_surface.api.user import User
from mangrove_surface.logger import log_exception, logger


class Controller:

    def __init__(
        self, surface, surface_url=None, token=None,
        username=None, password=None
    ):
        self._init_url(surface_url)
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._init_token(username, password, token)
        self.surface = surface
        self._last = datetime(1789, 7, 14, 0, 0)

    def _init_url(self, surface_url):
        if surface_url:
            self._surface_url = surface_url
        else:
            try:
                self._surface_url = os.environ["SURFACE_URL"]
            except KeyError:
                raise AttributeError(
                    "Surface's URL should be provided as an environment " +
                    "variable (`SURFACE_URL`) or as an explicit " +
                    "parameters (see `mangrove_surface.SurfaceClient` documentation)"
                )

        if not requests.get(self._surface_url).ok:
            raise IOError(
                "Surface's URL provided does not answer correctly, " +
                "please check it. If the problem persist then contact " +
                "your admin."
            )

    def check_license(self):
        def check_license():
            now = datetime.now()
            if (now - self._last).total_seconds() > 18000:
                self._last = now
                self.surface.admin.license_information()
        self.check_license = check_license

    def request(self, method, target=None, resource_manager=lambda resp: resp,
                check_license=True, **options):
        options["headers"] = self._headers
        if "data" in options.keys():
            options["data"] = json.dumps(options["data"])
        path = posixpath.join(self._surface_url, target)

        if method == "post" and check_license:
            self.check_license()
        logger.debug("REQUEST: {method} {path} :: {options}".format(
            method=method.upper(),
            path=path,
            options=json.dumps(options)
        ))
        resp = getattr(requests, method.lower())(path, **options)
        logger.debug("RESPONSE: {code}\n{response}".format(
            code=resp.status_code,
            response=resp.text.encode('utf-8')
        ))
        return resource_manager(resp)

    def _init_token(self, username, password, token):
        if username and password:
            resp = User.sign_in(self, username, password)
            User.errors_manager(resp)
            token = resp.headers["Authorization"]
        elif token:
            pass
        else:
            try:
                token = os.environ["SURFACE_TOKEN"]
            except KeyError:
                raise AttributeError(
                    "Surface's TOKEN should be provided as an " +
                    "environment variable (`SURFACE_TOKEN`) or as an " +
                    "explicit parameters (see `mangrove_surface.SurfaceClient` " +
                    "documentation)"
                )
        if not token.startswith("Bearer "):
            token = "Bearer " + token
        self._headers["Authorization"] = token
