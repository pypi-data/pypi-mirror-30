from mangrove_surface.api import Api


class Export(Api):

    resource = "exports"

    @classmethod
    def create(
        cls, controller, classifier_id, feature_set_id, name,
        modalities=[], bin_format="label", raw_variables=[],
        binned_variables=[]
    ):
        return cls.request(
            controller, "post",
            data={
                "name": name,
                "classifier_id": classifier_id,
                "feature_set_id": feature_set_id,
                "modalities": modalities,
                "raw_variables": raw_variables,
                "bin_format": bin_format,
                "binned_variables": binned_variables,
                "type": "data"
            }
        )
