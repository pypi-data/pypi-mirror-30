from mangrove_surface.api import Api
from mangrove_surface.logger import logger
import posixpath


class FeatureSet(Api):
    """
    Feature set resource

    ::

        {
          "created_at": "2018-03-14T12:01:24.964Z",
          "datasets": [
            {
              "central": true,
              "id": "cbf844ca-2c7d-4b3e-99cb-e31f5b0d7fa4",
              "keys": [
                "KEY"
              ],
              "name": "central"
            },
            ...
          ],
          "detailed_error": null,
          "errs": null,
          "id": "9842695c-cd43-46c0-b739-906fb8938606",
          "name": "Default",
          "nb_of_aggregates": 0,
          "status": "completed",
          "steps": {
            "completed": [
              "provision"
            ],
            "current": null,
            "failed": null,
            "missing": null,
            "next": []
          },
          "tags": null,
          "updated_at": "2018-03-14T12:01:25.070Z",
          "user_id": "bbd32850-0df0-4494-9c21-c338a2791020",
          "variables": [
            {
              "dataset_name": "peri",
              "id": "44f14fcc-2472-4fa0-87c4-43a4d0a4e53d",
              "name": "Date",
              "type": "timestamp",
              "use": true
            },
            ...
          ]
        }
    """

    resource = "feature_sets"

    @classmethod
    def create(cls, controller, name, project_id, datasets=[]):
        """
        :param controller: the controller
        :param name: feature set name
        :param project_id: id of the project
        :param datasets: a list of dataset like ::

            {
                "id": "dataset_id",
                "keys": ["list", "of", "keys"],
                "central": True or False
            }
        """
        return cls.request(
            controller, "post",
            data={
                "name": name,
                "project_id": project_id,
                "datasets": datasets
            }
        )

    @classmethod
    def generate_aggregates(
        cls, controller, feature_set_id, nb_of_requested_aggregates
    ):
        return cls.request(
            controller, "patch",
            target=posixpath.join(cls.resource, feature_set_id),
            data={
                "nb_of_aggregates": nb_of_requested_aggregates
            }
        )

    @classmethod
    def make_changes(cls, controller, feature_set_id, *changes):
        """
        :param changes: is a tuple of dictionaries like::

                {
                  "attribute": "use",
                  "value": false,
                  "variable_ids": ["var1_id", "var2_id", ...]
                }
        """
        return cls.request(
            controller, "patch",
            target=posixpath.join(cls.resource, feature_set_id),
            data={
                "changes": list(changes)
            }
        )

    @classmethod
    def make_changes_and_generate_aggregates(
        cls, controller, feature_set_id,
        nb_of_requested_aggregates, *changes
    ):
        return cls.request(
            controller, "patch",
            target=posixpath.join(cls.resource, feature_set_id),
            data={
                "nb_of_aggregates": nb_of_requested_aggregates,
                "changes": list(changes)
            }
        )

    @classmethod
    def clone(cls, controller, feature_set_id, name, tags=[]):
        return cls.request(
            controller, 'post',
            target=posixpath.join(cls.resource, feature_set_id, "copy"),
            data={"name": name, "tags": tags}
        )

    @classmethod
    def get_all(cls, controller, project_id=None):
        query = {
            'project_id': project_id
        } if project_id else None
        return cls.request(controller, 'get', params=query)
