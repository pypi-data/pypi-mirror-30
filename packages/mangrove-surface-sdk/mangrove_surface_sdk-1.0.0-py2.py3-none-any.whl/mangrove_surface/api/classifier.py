from mangrove_surface.api import Api
import posixpath


class Classifier(Api):
    """
    Classifier resource::

        {
          "created_at": "2018-03-14T12:02:24.725Z",
          "detailed_error": null,
          "errs": null,
          "feature_set_id": "9842695c-cd43-46c0-b739-906fb8938606",
          "id": "888fab8c-7d06-4b4a-b571-0d33b890b934",
          "name": "OMC-20180314-14:02:35",
          "nb_of_max_variables": null,
          "outcome": "House_Owner",
          "path": "files/888fab8c-7d06-4b4a-b571-0d33b890b934",
          "signed_url": "http://mang-ai-4-0.sandbox.mangrove.lan/files/888fab8c-7d06-4b4a-b571-0d33b890b934?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=QXZMV3CNUCJOWQVVNKMD%2F20180314%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20180314T144735Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=d43658d982a0133b68b6306d437dbed8708e9950b42b94b4b4d8b673f91cf187",
          "status": "completed",
          "steps": {
            "completed": [
              "modelize"
            ],
            "current": null,
            "failed": null,
            "missing": null,
            "next": []
          },
          "tags": [],
          "univariate_supervised_report": {
            "classifier_id": "888fab8c-7d06-4b4a-b571-0d33b890b934",
            "dictionary_title": "central",
            "id": "71d5736f-cd14-4694-be0e-89c46abad2b9",
            "target_modalities": [
              "N",
              "Y"
            ],
            "type": "univariate_supervised",
            "variables": [
              {
                "groups_attributes": [
                  {
                    "coverage": 0.116404,
                    "frequency": 2478,
                    "target_distribution": {
                      "N": 0.0464084,
                      "Y": 0.953592
                    },
                    "value_list": [
                      "Special purpose vehicle",
                      "MPV"
                    ]
                  }, ...
                ],
                "id": "fad8f86e-d0b6-4e1c-87e0-a7960c609232",
                "level": 0.473592,
                "name": "Car_Type",
                "nb_of_groups": 7,
                "type": "categorical"
              }, ...
            ],
            "version": "V8_0"
          },
          "updated_at": "2018-03-14T12:02:24.725Z",
          "user_id": "bbd32850-0df0-4494-9c21-c338a2791020",
          "variables": [
            {
              "id": "4313ad08-2903-47ac-a109-578d47260437",
              "level": 0.473592,
              "maximum_a_posteriori": true,
              "name": "Car_Type",
              "weight": 0.914175
            }, ...
          ]
        }
    """

    resource = "classifiers"

    @classmethod
    def create(
        cls, controller, name, feature_set_id, outcome, tags=[],
        maximum_features=None
    ):
        data = {
            "name": name,
            "tags": tags,
            "outcome": outcome,
            "feature_set_id": feature_set_id,
        }
        if maximum_features:
            data["nb_of_max_variables"] = maximum_features

        return cls.request(controller, "post", data=data)

    @classmethod
    def rename(cls, controller, classifier_id, name):
        data = {
            "name": name
        }

        return cls.request(
            controller, "patch",
            target=posixpath.join(cls.resource, classifier_id), data=data
        )

    @classmethod
    def delete(cls, controller, classifier_id):
        return cls.request(
            controller, "delete",
            target=posixpath.join(cls.resource, classifier_id)
        )

    @classmethod
    def get_all(cls, controller, project_id):
        return cls.request(
            controller, "get", params={'project_id': project_id}
        )
