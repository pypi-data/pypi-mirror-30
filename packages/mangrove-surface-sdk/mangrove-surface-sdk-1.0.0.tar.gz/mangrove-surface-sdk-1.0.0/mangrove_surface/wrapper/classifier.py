import os.path as path
import requests
import warnings
from copy import deepcopy
from datetime import datetime
from mangrove_surface.wrapper import Wrapper, run_once, should_be_terminated
from mangrove_surface.logger import logger, log_exception
from mangrove_surface.api.classifier_evaluation_report import \
    ClassifierEvaluationReport
from mangrove_surface.wrapper.classifier_evaluation_report import \
    ClassifierEvaluationReportWrapper
from mangrove_surface.wrapper.export import ExportWrapper
from mangrove_surface.api.export import Export
from mangrove_surface.misc import iter_progress_bar


class MangroveSchemaDoesNotExist(KeyError):
    pass


class AssessmentDoesNotExist(KeyError):
    pass


class ExportDoesNotExist(KeyError):
    pass


class ClassifierWrapper(Wrapper):
    """
    Classifier resource

    A classifier provides

    * the list relevants features (including level, weight, discretization
      attributes)
    * the assessments over each train/test schemas
    * method to export scores over
    * method to improve classifier

    """

    def __init__(self, classifier_resource, collection):
        Wrapper.__init__(self, classifier_resource, collection)
        from mangrove_surface.api.feature_set import FeatureSet
        from mangrove_surface.wrapper.feature_set import FeatureSetWrapper
        fs = FeatureSet.retrieve(
            self._controller, self.api_resource.feature_set_id()
        )
        self._fs = FeatureSetWrapper(fs, self.accessor)

    @run_once
    def _extra_init_(self):
        Wrapper._extra_init_(self)
        self._fs._link_to_classifier(self)

        type_parts_mapper = {
            "continuous": "intervals_attributes",
            "categorical": "groups_attributes"
        }
        type_nb_parts_mapper = {
            "continuous": "nb_of_intervals",
            "categorical": "nb_of_groups"
        }
        self._features = {
            feat["name"]: {
                "id": feat["id"],
                "name": feat["name"],
                "level": feat["level"],
                "weight": feat["weight"],
                "maximum_a_posteriori": feat["maximum_a_posteriori"],
                "parts": feat[type_parts_mapper[feat["type"]]],
                "nb_parts": feat[type_nb_parts_mapper[feat["type"]]]
            }
            for feat in self.api_resource.variables()
        }

    def update_name(self, new_name):
        """
        Update the classifier name

        :param new_name: new classifier name
        """
        self.api_resource.rename(
            self._controller, self.api_resource.id(), new_name
        )
        self.update()

    def outcome(self):
        """
        Outcome field predicted by the current classifier
        """
        return self.api_resource.outcome()

    @should_be_terminated
    def level(self, name):
        """
        Return the level of the feature named ``name``

        :param name: feature name

        The level indicates the correlation between the feature and the outcome
        """
        if name in self._features.keys():
            return self._features[name]["level"]
        else:
            return 0.0

    @should_be_terminated
    def weight(self, name):
        """
        Return the weight of the feature named ``name``

        :param name: feature name

        The weight indicates how the feature discriminates more than others
        relevant features (with level > 0)
        """
        if name in self._features.keys():
            return self._features[name]["weight"]
        else:
            return 0.0

    @should_be_terminated
    def is_maximum_a_priori(self, name):
        return self._features[name]["maximum_a_priori"]

    @should_be_terminated
    def discretization_attribute(self, name):
        """
        Return the discretization attribute of the contributive feature
        ``name``

        :param name: feature name

        ::

            >>> classifier.discretization_attribute("Car_Type")
            [
                {
                    'coverage': 0.0248497,
                    'frequency': 529,
                    'target_distribution': {
                        '0': 0.837429,
                        '1': 0.162571
                    },
                    'value_list': ['Full-size luxury car']
                },
                ...
            ]

        """
        return self._features[name]["parts"]

    @should_be_terminated
    def set_unused(self, name):
        """
        Set feature ``name`` unused

        :param name: feature name
        """
        self._fs.central().set_unused(name)

    def nb_aggregates(self):
        """
        Return the number of aggregates
        """
        return self.feature_set().api_resource.nb_of_aggregates()

    def improve(self, name=None, tags=[], nb_aggregates=None,
                maximum_features=None):
        """
        Create a new classifier

        :param name: (*optional*) classifier name
        :param tags: (*optional*) list of project tag
        :param nb_aggregates: (*optional*) number of aggregates generated for
            the new classifier
        :param maximum_features: (*optional*) maximal number of features used
            by the new classifier

        :raise MangroveError: if the number of requested aggregates is provided and
            it is smaller than ``.nb_aggregates()``
        """
        return self._fs.fit_classifier(
            name=name, tags=tags, nb_aggregates=nb_aggregates,
            maximum_features=maximum_features
        )

    @should_be_terminated
    def feature_set(self):
        """
        Return the underlying feature set

        .. note::

            This feature set could be used to change type, unused some features
        """
        return self._fs

    @should_be_terminated
    def download(self, filepath):
        """
        Download the classifier

        :param filepath: the filepath where store the classifier

        """
        from_url = self.api_resource.signed_url()

        logger.debug(
            'Download classifier `{classifier}`: {from_path} > {to_path}'.
            format(
                from_path=from_url, to_path=filepath, classifier=self.name()
            )
        )

        response = requests.get(
            from_url, stream=True
        )

        if not response.ok:
            log_exception(response.raise_for_status)()

        with open(filepath, 'wb') as handle:
            size = response.headers["content-length"]
            for block in iter_progress_bar(
                response.iter_content(1024),
                path.basename(filepath) + ': ',
                size, modulo=1024
            ):
                handle.write(block)

        logger.debug('Classifier `{classifier}` Downloaded'.format(
            classifier=self.name()
        ))

    @should_be_terminated
    def features(self):
        """
        List all the features used by the current classifier

        ::

            >>> classifier.features()
            [
                {
                    'level': 0.103459,
                     'maximum_a_posteriori': True,
                     'name': 'Car_Type',
                     'nb_parts': 4,
                     'parts': [
                         {
                            'coverage': 0.0248497,
                            'frequency': 529,
                            'target_distribution': {
                                '0': 0.837429,
                                '1': 0.162571
                            },
                            'value_list': ['Full-size luxury car']
                        },
                        ...
                    ],
                    'weight': 0.832425
                },
                ...
            ]

        """
        return [
            {
                "name": feat["name"],
                "level": feat["level"],
                "weight": feat["weight"],
                "maximum_a_posteriori": feat["maximum_a_posteriori"],
                "parts": deepcopy(feat["parts"]),
                "nb_parts": feat["nb_parts"]
            }
            for feat in self._features.values()
        ]

    @should_be_terminated
    def feature(self, name):
        """
        Information about feature ``name``

        It returns level, weight, discretization attributes.

        :param name: feature name

        ::

            >>> classifier.feature('Car_Type')
            {
                'level': 0.103459,
                 'maximum_a_posteriori': True,
                 'name': 'Car_Type',
                 'nb_parts': 4,
                 'parts': [
                     {
                        'coverage': 0.0248497,
                        'frequency': 529,
                        'target_distribution': {
                            '0': 0.837429,
                            '1': 0.162571
                        },
                        'value_list': ['Full-size luxury car']
                    },
                    ...
                ],
                'weight': 0.832425
            }

        """
        feat = self._features[name]
        return {
            "name": feat["name"],
            "level": feat["level"],
            "weight": feat["weight"],
            "maximum_a_posteriori": feat["maximum_a_posteriori"],
            "parts": deepcopy(feat["parts"]),
            "nb_parts": feat["nb_parts"]
        }

    def assessments(self):
        return [ClassifierEvaluationReportWrapper(cer, self)
                for cer in ClassifierEvaluationReport.retrieve_all(
                    self._controller, classifier_id=self.api_resource.id()
        )]

    def assessment(self, name):
        assessments = list(
            filter(lambda cl: cl.name() == name, self.assessments())
        )
        if len(assessments) == 0:
            raise AssessmentDoesNotExist(name + ' does not exists')
        elif len(assessments) > 1:
            warnings.warn("There is several classifier called `%s`! " % name +
                          "The 1st has been selected.")
        return assessments[0]

    def compatible_schemas(self, test=True, export=True):
        """
        List compatible schemas (with there type)
        """
        return [
            {
                "name": schm["name"],
                "type": schm["type"]
            }
            for schm in self.accessor.api_resource.schemas()
        ]

    def add_schema(self, type_schm, schema, name=None):
        """
        Upload a new schema of datasets

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
                        "separator": ",", # could be `|`, `,`, `;` or `\t`
                    }, ...
                ]
            }

        """
        assert(type_schm in ["export", "test"]), \
            "The schema type should be `export` or `test`"

        self.accessor.create_schema(type_schm, schema, name=name)

    def add_schema_and_export(
            self, schema, name=None, modalities=[], bin_format="label",
            raw_variables=[], binned_variables=[], predicted_modality=False
    ):
        """
        Upload a new schema and export it

        :param schema: a python dictionary of datasets
            (see :meth:`~.ClassifierWrapper.add_schema`:)
        :param name: (*optional*) the schema name
        :param modalities: (*optional*) the modalities scored. If no modality
            is provided then scores are not provided (only variables)
        :param raw_variables: the list of variables to export as raw value
        :param binned_variables: the list of variables to export as binned
            value
        :param bin_format: (*default*: ``label``) select how to express the
            binned variables. ``label`` (*default*) to express value as its
            intervals or groups, or ``id`` to express value as a concise value
        :param predicted_modality: provided a column with the predicted value
            if ``predicted_modality==True`` (*default*
            ``predicted_modality==False``)
        """
        if not name:
            now = datetime.now().isoformat()
            name = "FeatureSet-" + now
        self.add_schema("export", schema, name=name)
        return self.compute_export(
            name, modalities=modalities, bin_format=bin_format,
            raw_variables=raw_variables, binned_variables=binned_variables
        )

    def compute_assessments(self, schm_name, outcome_modality=None):
        """
        Compute assessment over schema named ``schm_name`` (focus on modality
        ``outcome_modality``)

        :param schm_name: name of the schema used to compute assessments
        :param outcome_modality: the modality used to compute assessments (by
            *default* assessments is computed over the main modality)
        """
        schm = self.accessor.schema(schm_name)
        if not outcome_modality:
            outcome_modality = self.accessor._schema()["outcome_modality"]
        fs_id = schm.resource["feature_set_ids"][0]
        cl_id = self.api_resource.id()
        ce = ClassifierEvaluationReportWrapper(
            ClassifierEvaluationReport.create(
                self._controller, fs_id, cl_id, outcome_modality
            ),
            self
        )
        collection = self.accessor
        collection.api_resource.update_add_classifier_evaluation_report(
            self._controller,
            collection.api_resource.id(), ce.api_resource.id()
        )
        return ce

    def compute_export(
        self, schm_name, export_name=None, modalities=[],
        bin_format="label", raw_variables=[], binned_variables=[],
        predicted_modality=False
    ):
        """
        Compute a new export

        :param schm_name: the dataset schema which is exported
        :param export_name: name of the export
        :param modalities: (*optional*) the modalities scored. If no modality
            is provided then scores are not provided (only variables)
        :param raw_variables: the list of variables to export as raw value
        :param binned_variables: the list of variables to export as binned
            value
        :param bin_format: (*default*: ``label``) select how to express the
            binned variables. ``label`` (*default*) to express value as its
            intervals or groups, or ``id`` to express value as a concise value
        :param predicted_modality: provided a column with the predicted value
            if ``predicted_modality==True`` (*default*
            ``predicted_modality==False``)
        """
        schm = self.accessor.schema(schm_name)
        fs_id = schm.resource["feature_set_ids"][0]
        cl_id = self.api_resource.id()

        if not export_name:
            now = datetime.now().isoformat()
            export_name = "export-" + now

        if predicted_modality:
            raw_variables += ["Predicted" + self.outcome()]

        exp = ExportWrapper(
            Export.create(
                self._controller, cl_id, fs_id, export_name,
                modalities=modalities, bin_format="label",
                raw_variables=raw_variables,
                binned_variables=binned_variables
            ),
            self
        )
        self.accessor.api_resource.update_add_export(
            self._controller, self.accessor.api_resource.id(),
            exp.api_resource.id()
        )
        logger.info("Export {name} created".format(name=export_name))
        return exp

    def export(self, name):
        exports = list(
            filter(lambda ex: ex.name() == name, self.exports())
        )
        if len(exports) == 0:
            raise ExportDoesNotExist(name + ' does not exists')
        elif len(exports) > 1:
            warnings.warn("There is several exports called `%s`! " % name +
                          "The 1st has been selected.")
        return exports[0]

    def exports(self):
        """
        List all exports
        """
        return [
            ExportWrapper(export, self)
            for export in Export.retrieve_all(
                self._controller, classifier_id=self.api_resource.id()
            )
        ]
