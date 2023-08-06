from mangrove_surface.wrapper import Wrapper


class DatasetWrapper(Wrapper):
    """
    Data set resource
    """

    def name(self):
        return self.api_resource.name()
