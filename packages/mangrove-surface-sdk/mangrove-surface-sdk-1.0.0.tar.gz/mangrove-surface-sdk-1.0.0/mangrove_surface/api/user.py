from mangrove_surface.api import Api


class User(Api):

    resource = "users"

    @classmethod
    def sign_in(cls, controller, username, password):
        return controller.request(
            "post", target=cls.resource + "/sign_in", data={
                "username": username,
                "password": password
            }
        )

    @classmethod
    def create(cls, controller, username, password):
        return cls.request(controller, "post", data={
            "username": username,
            "password": password
        })

    @classmethod
    def retrieve_me(cls, controller):
        return cls.request(controller, "get", target=cls.resource + "/me")

    def __repr__(self):
        s = "(admin)" if self.is_admin() else ""
        return self.username() + s
