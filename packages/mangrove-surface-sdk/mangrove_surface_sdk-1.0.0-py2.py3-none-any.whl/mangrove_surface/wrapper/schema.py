from mangrove_surface.wrapper import Wrapper
from copy import deepcopy
from mangrove_surface.wrapper.feature_set import FeatureSetWrapper
from mangrove_surface.api.feature_set import FeatureSet
from mangrove_surface.wrapper.dataset import DatasetWrapper
from mangrove_surface.api.dataset import Dataset


class SchemaWrapper(Wrapper):

    def __init__(self, api_resource, collection):
        Wrapper.__init__(self, collection.api_resource, collection)
        self.resource = api_resource

    def name(self):
        return self.resource["name"]

    __repr__ = name

    def type(self):
        return self.resource["type"]

    def is_train(self):
        return self.type() == "train"

    def is_test(self):
        return self.type() == "test"

    def is_export(self):
        return self.type() == "export"

    def describe(self):
        return deepcopy(self.resource)

    def feature_sets(self):
        return [
            FeatureSetWrapper(
                FeatureSet.retrieve(self._controller, fs_id), self.accessor
            )
            for fs_id in self.resource["feature_set_ids"]
        ]

    def datasets(self):
        return [
            DatasetWrapper(
                Dataset.retrieve(self._controller, table["dataset_id"]), self
            )
            for table in self.resource["tables"]
        ]
