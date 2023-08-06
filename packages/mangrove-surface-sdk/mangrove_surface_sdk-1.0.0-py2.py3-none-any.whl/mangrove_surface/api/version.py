from mangrove_surface.api import Api
import mangrove_surface


class Version(Api):
    """
    Version resource
    """

    resource = "versions"

    @classmethod
    def retrieve(cls, controller):
        def resource_manager(resp):
            cls.errors_manager(resp, over_list=True)
            versions = resp.json()
            versions.append(
                {"name": "mang_sdk", "version": mangrove_surface.__version__}
            )
            return versions
        return cls.request(
            controller, "get", resource_manager=resource_manager
        )
