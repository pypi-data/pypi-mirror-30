from mangrove_surface.api import Api
import posixpath


class CollectionDoesNotExist(ValueError):
    pass


class Collection(Api):
    """
    Collection resource::

        {
          "created_at": "2018-03-12T14:44:53.518Z",
          "description": "",
          "id": "458b2379-0aa5-404d-81fe-95dd95a81029",
          "name": "Collection-0",
          "project_id": "c78d3c0b-d72a-48cb-90b2-b4a4a63d971c",
          "schemas": [
            {
              "collection_id": "03e92139-7b5a-44b8-995d-3d6bac2df809",
              "feature_set_ids": [
                "b7de7a44-be74-43fe-bb0e-59c63dcde783"
              ],
              "id": "ddbb3898-1531-4896-af3b-cdc2b801d5b7",
              "name": "Schema-20180322-14:57:18",
              "outcome": "LABEL",
              "outcome_modality": "Y",
              "status": "completed",
              "tables": [
                {
                  "dataset_id": "20ddcea4-230c-4e14-8a22-4e7e11279228",
                  "dataset_name": "Central",
                  "id": "726ed914-633a-474f-af68-14ffbb4b32b8",
                  "keys": [
                    "KEY"
                  ],
                  "type": "central"
                },
                {
                  "dataset_id": "f85b3430-0623-45ce-80f8-598776addc38",
                  "dataset_name": "Peri",
                  "id": "2a69ed1e-350b-401a-8ead-e5fb094e35d7",
                  "keys": [
                    "KEY"
                  ],
                  "type": "peripheral"
                }
              ],
              "type": "train"
            }
          ],
          "tags": null,
          "updated_at": "2018-03-12T14:44:53.518Z",
          "user_id": "15e8769b-d2f8-47dd-95ab-1086966aa5fa"
        }

    """

    resource = "collections"

    @classmethod
    def create(cls, controller, project_id, name,  description):
        return cls.request(
            controller, "post",
            params={"project_id": project_id},
            data={
                "name": name,
                "description": description
            }
        )

    @classmethod
    def create_schema(
        cls, controller, collection_id, type_schm, name,
        outcome=None, outcome_modality=None
    ):
        assert(type_schm in ["train", "test", "export"])
        data = {"type": type_schm, "name": name}
        if type_schm == "train":
            data["outcome"] = outcome
            data["outcome_modality"] = outcome_modality

        return cls.request(
            controller, "post", data=data,
            target=posixpath.join(cls.resource, collection_id, "schemas")
        )

    @classmethod
    def delete_schema(cls, controller, collection_id, schema_id):
        return cls.request(
            controller, "delete",
            target=posixpath.join(
                cls.resource, collection_id, "schemas", schema_id
            )
        )

    @classmethod
    def update_schema_add_table(
        cls, controller, collection_id, schema_id, central, dataset_id, *keys
    ):
        return cls.request(
            controller, "patch",
            target=posixpath.join(
                cls.resource, collection_id, "schemas", schema_id
            ), data={
                "tables_attributes": [{
                    "type": "central" if central else "peripheral",
                    "dataset_id": dataset_id,
                    "keys": list(keys)
                }]
            }
        )

    @classmethod
    def update_schema_remove_table(
        cls, controller, collection_id, schema_id, table_id
    ):
        return cls.request(
            controller, "delete", target=posixpath.join(
                cls.resource, collection_id, "schemas", schema_id,
                "tables", table_id
            )
        )

    @classmethod
    def update_schema_add_feature_set(
        cls, controller, collection_id, schema_id, feature_set_id
    ):
        return cls.request(
            controller, "patch", data={
                "feature_set_ids": [feature_set_id]
            },
            target=posixpath.join(
                cls.resource, collection_id, "schemas", schema_id
            )
        )

    @classmethod
    def update_schema_remove_feature_set(
        cls, controller, collection_id, schema_id, feature_set_id
    ):
        return cls.request(
            controller, "delete",
            target=posixpath.join(
                cls.resource, collection_id, "schemas", schema_id,
                "feature_set", feature_set_id
            )
        )

    @classmethod
    def update_add_classifier(cls, controller, collection_id, classifier_id):
        return cls.request(
            controller, "patch",
            target=posixpath.join(cls.resource, collection_id),
            data={"classifier_ids": [classifier_id]}
        )

    @classmethod
    def update_add_classifier_evaluation_report(
            cls, controller, collection_id, cer_id
    ):
        return cls.request(
            controller, "patch",
            target=posixpath.join(cls.resource, collection_id),
            data={"classifier_evaluation_ids": [cer_id]}
        )

    @classmethod
    def update_add_export(
            cls, controller, collection_id, export_id
    ):
        return cls.request(
            controller, "patch",
            target=posixpath.join(cls.resource, collection_id),
            data={"export_ids": [export_id]}
        )

    @classmethod
    def add_feature_sets(cls, controller, collection_id, *feature_set_ids):
        return cls.request(
            controller, "post", data=list(feature_set_ids),
            target=posixpath.join(cls.resource, collection_id, "feature_sets")
        )

    @classmethod
    def remove_feature_set(cls, controller, collection_id,
                           feature_set_id):
        return cls.request(
            controller, "delete",
            target=posixpath.join(
                cls.resource, collection_id, "feature_sets", feature_set_id
            )
        )

    def is_failed(self):
        return False
    is_running = is_failed

    def is_completed(self):
        return True
