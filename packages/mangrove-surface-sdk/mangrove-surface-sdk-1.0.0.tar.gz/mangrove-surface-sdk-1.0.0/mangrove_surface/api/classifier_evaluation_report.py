from mangrove_surface.api import Api
import posixpath
import sys
if sys.version_info[0] >= 3:
    from inspect import signature
else:
    from funcsigs import signature


class ClassifierEvaluationReport(Api):
    """
    Classifier Evaluation Report resource

    """

    resource = "classifier_evaluation_reports"

    @classmethod
    def create(cls, controller, feature_set_id, classifier_id,
               outcome_modality):
        return cls.request(
            controller, "post",
            data={
                "feature_set_id": feature_set_id,
                "classifier_id": classifier_id,
                "outcome_modality": outcome_modality
            }
        )
