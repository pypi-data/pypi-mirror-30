from datetime import datetime
from mangrove_surface.api.dataset import Dataset
from mangrove_surface.api.feature_set import FeatureSet
from mangrove_surface.logger import logger
from mangrove_surface.wrapper import Wrapper
from mangrove_surface.wrapper.feature_set import FeatureSetWrapper
from mangrove_surface.wrapper.schema import SchemaWrapper


class CollectionWrapper(Wrapper):
    """
    Collection

    A collection is a set of dataset schemas which are similars.
    """

    def is_completed(self):
        train_schm = list(filter(
            lambda schm: schm["type"] == "train",
            self.api_resource.json["schemas"]
        ))
        if len(train_schm) != 1 or \
                train_schm[0]["feature_set_ids"] == None or \
                train_schm[0]["feature_set_ids"] == []:
            return False
        else:
            mang = self.accessor.accessor
            fs = FeatureSet.retrieve(
                mang._controller, train_schm[0]["feature_set_ids"][0]
            )
            return fs.is_completed()

    def schema(self, name):
        """
        Return schema named ``name``

        :param name: the name of the requested schema
        """
        schms = list(filter(
            lambda schm: schm.resource["name"] == name,
            self.schemas()
        ))
        if len(schms) == 0:
            raise Exception("Collection `%s` does not exist" % name)
        return schms[0]

    def _schema(self):
        schms = list(filter(
            lambda schm: schm["type"] == "train",
            self.api_resource.json["schemas"]
        ))
        if len(schms) == 0:
            raise Exception("Collection is not initialized")
        return schms[0]

    def schemas(self):
        """
        List all schemas of the current collection
        """
        return [
            SchemaWrapper(schm, self) for schm in self.api_resource.schemas()
        ]

    def create_schema(self, type_schm, schema, name=None, check=True):
        """
        Create a new schema into the current collection

        :param type_schm: ``train``, ``test`` or ``export``
        :param schema: a python dictionary recording datasets like this

        ::

            {
                "tags": ["dataset", "tag"],
                "datasets": [
                    {
                        "name": "Dataset Name",
                        "filepath": "/path/to/dataset.csv",
                        "tags": ["optional", "tags"],
                        "central": True | False,
                        "keys: ["index"], # optional if there is only
                                          # one dataset
                        "separator": ",", # could be `|`, `,`, `;` or ` `
                    }, ...
                ]
            }

        """
        if "keys" not in schema["datasets"][0]:
            assert(len(schema["datasets"]) == 1), \
                "keys are optional if and only if there is one dataset"
            schema["datasets"][0]["keys"] = []

        if check:
            b = False
            for dataset in schema["datasets"]:
                b = b ^ dataset["central"]
                assert(isinstance(dataset["keys"], (list, tuple))), \
                    "Keys have to be a list of field"
            assert(b), \
                "Schema have to contain one and only one central dataset"

            schms = self.schemas()
            if len(schms) > 0:
                oschm = schms[0]

                other_names = set(map(lambda ds: ds.name(), oschm.datasets()))
                names = set(map(lambda ds: ds["name"], schema["datasets"]))
                assert(other_names == names), "Dataset names have to be sames"

        outcome, outcome_modality = \
            (schema["outcome"], schema["outcome_modality"]) \
            if "outcome" in schema.keys() else (None, None)

        if not name:
            now = datetime.now().isoformat()
            name = "FeatureSet-" + now

        schm = self.api_resource.create_schema(
            self._controller, self.api_resource.id(),
            type_schm, name, outcome=outcome, outcome_modality=outcome_modality
        )

        for ds in schema["datasets"]:
            tags = ds["tags"] if "tags" in ds.keys() else []
            self._add_dataset(
                schm, ds["central"], ds["name"], ds["filepath"],
                separator=ds["separator"], keys=ds["keys"], tags=tags,
                field=outcome if ds["central"] else None
            )
        schm_id = schm.id()
        schm = list(filter(
            lambda schm: schm["id"] == schm_id,
            self.api_resource.schemas()
        ))[0]
        fs = FeatureSetWrapper(FeatureSet.create(
            self._controller, name,
            self.accessor.api_resource.id(),
            datasets=[{
                "id": ds["dataset_id"],
                "keys": ds["keys"],
                "central": ds["type"] == "central"
            } for ds in schm["tables"]]
        ), self)
        self.api_resource.update_schema_add_feature_set(
            self._controller, self.api_resource.id(), schm_id,
            fs.api_resource.id()
        )
        self.update()
        return fs

    def _add_dataset(
        self, schm, central, name, filepath, separator=",", field=None,
        keys=[], tags=[], chunksize=1073741824
    ):
        """
        Add a dataset to the schema ``schm``

        :param schm: the schema to update
        :param central: ``True``if the dataset is central; ``False`` if it is
            peripheral
        :param name: the dataset name
        :param filepath: the filepath used to upload the dataset
        :param separator: the dataset separator (*default*: ``,``)
        :param field: if the dataset is ``central`` you could provide a
            field and it provides modalities of it
        :param keys: list of join key
        :param tags: the dataset tags
        :param chunksize: (*default value*: ``1073741824``) the chunk size use
            to upload

        """
        mang = self.accessor.accessor
        dataset = Dataset.create_upload_patch_dataset(
            mang._controller, name, filepath, field=field, tags=tags,
            keys=keys, separator=separator
        )
        self.api_resource.update_schema_add_table(
            mang._controller, self.api_resource.id(), schm.id(), central,
            dataset.id(), *keys
        )
        logger.info("Dataset created (%s)" % name)
        self.update()
