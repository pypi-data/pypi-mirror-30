from mangrove_surface.api import Api


class Token(Api):

    resource = "tokens"

    @classmethod
    def create(cls, controller, name, expires_at):
        return cls.request(controller, "post", data={
            "name": name,
            "expires_at": expires_at
        })

    @classmethod
    def edit_token(cls, controller, token_id, name=None, expires_at=None):
        return cls.request(
            controller, "patch", target=token_id, data=dict(filter(
                lambda x: x[1],
                {
                    "name": name,
                    "expires_at": expires_at
                }.items()
            ))
        )
