import posixpath
import sys
from mangrove_surface.api import Api
from mangrove_surface.logger import logger

if sys.version_info[0] >= 3:
    from inspect import signature
else:
    from funcsigs import signature


class Project(Api):
    """
    Project resource::

        {
          "id": "0775c6a8-f9cb-4380-8aa5-d6a7dd42caf3",
          "user_id": "284e4810-975f-4ce9-ab22-8782a3e0f2d3",
          "name": "Project Name",
          "description": "Amazing description",
          "tags": ["blue", "white", "red"],
          "created_at": "2018-03-06T10:25:37.271Z",
          "updated_at": "2018-03-06T10:25:37.271Z"
        }

    """

    resource = 'projects'

    @classmethod
    def create(cls, controller, name, description, tags=[]):
        resp = cls.request(controller, "post", data={
            "name": name,
            "description": description,
            "tags": tags
        })
        logger.info("Project `%s` created" % name)
        return resp

    @classmethod
    def rename(cls, controller, project_id, name):
        resp = cls.request(
            controller, 'patch',
            target=posixpath.join(cls.resource, project_id),
            data={"name": name}
        )
        return resp

    @classmethod
    def update_description(cls, controller, project_id, description):
        return cls.request(
            controller, 'patch',
            target=posixpath.join(cls.resource, project_id),
            data={"description": description}
        )

    @classmethod
    def update_tags(cls, controller, project_id, tags=[]):
        return cls.request(
            controller, 'patch',
            target=posixpath.join(cls.resource, project_id),
            data={"tags": tags}
        )
