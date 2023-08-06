from datetime import datetime
from mangrove_surface.api.classifier import Classifier
from mangrove_surface.logger import logger
from mangrove_surface.wrapper import Wrapper, run_once, should_be_terminated
from mangrove_surface.wrapper.classifier import ClassifierWrapper
from mangrove_surface.api.feature_set import FeatureSet
from mangrove_surface.api.dataset import Dataset
from mangrove_surface.wrapper.misc import waiter


class MangroveChangeForbidden(Exception):
    pass


class FeatureSetWrapper(Wrapper):
    """
    Feature set resource

    A feature set is a set of frames (one for each data set).
    A frame contains variables and its metadata (type, use or not).

    It is used to customize data, generate aggregates and to train classifiers.
    """

    def __init__(self, feature_set_resource, collection):
        Wrapper.__init__(self, feature_set_resource, collection)
        self._frames = {}

    @run_once
    def _extra_init_(self):
        Wrapper._extra_init_(self)
        self._is_linked_to_classifier = False

        nb_agg = self.api_resource.nb_of_aggregates()
        for ds in self.api_resource.datasets():
            self._frames[ds["tablename"]] = self._Frame(
                ds, (ds["central"] or ((nb_agg == 0) and (not ds["central"]))),
                self
            )
            if ds["central"]:
                self._central = self._frames[ds["tablename"]]

        for v in self.api_resource.variables():
            frame = self._frames[v["tablename"]]
            frame._variables[v["name"]] = v

    def _link_to_classifier(self, classifier):
        self._classifier = classifier
        self._is_linked_to_classifier = True

    @should_be_terminated
    def central(self):
        """
        Return the central frame

        The central frame is the one used to train classifiers.
        """
        return self._central

    @should_be_terminated
    def frame(self, name):
        """
        Return the frame named ``name``

        :param name: data (set) frame name
        """
        return self._frames[name]

    @should_be_terminated
    def frames(self):
        """
        List all frames
        """
        return list(self._frames.values())

    @should_be_terminated
    def generate_aggregates(self, n):
        """
        Generate a new feature set with ``n`` aggregates

        :param n: number of aggregates requested (a non-negative integer)

        """
        if self == self.accessor.accessor.default_feature_set():
            raise Exception(
                "The default feature set cannot be overwrite! " +
                "You have to clone it"
            )
        fs = self.clone()
        fs.wait_until_terminated()
        fs.api_resource.make_changes_and_generate_aggregates(
            self._controller,
            fs.api_resource.id(), n, *[
                {
                    "variable_ids": [fs._frames[frame]._variables[k[0]]["id"]],
                    "variable_names":
                        [fs._frames[frame]._variables[k[0]]["name"]],
                    "attribute": k[1],
                    "value": self._frames[frame]._variables[k[0]][k[1]]
                }
                for frame in self._frames.keys()
                for k in self._frames[frame]._modifications.keys()
            ]
        )
        fs.update()
        fs.wait_until_terminated()
        fs.__init__(fs.api_resource, fs.accessor)
        return fs

    def fit_classifier(self, name=None, tags=[], nb_aggregates=None,
                       maximum_features=None):
        """
        Fit a new classifier

        :param name: (*optional*) classifier name (by default the name will be
            the project name concatenated with the current time
        :param tags: the classifier tags
        :param nb_aggregates: used to generates ``nb_aggregates`` aggregates on
            the central frame used to train the classifier
        :param maximum_features: used to allow at most ``maximum_features``
            features in the new classifier
        """
        if nb_aggregates:
            fs = self.generate_aggregates(nb_aggregates)
        elif self.is_modified():
            fs = self.save()
        else:
            fs = self
        if not name:
            now = datetime.now().isoformat()
            name = self.accessor.accessor.api_resource.name() + "-" + now

        outcome = self.accessor._schema()["outcome"]
        outcome_modality = self.accessor._schema()["outcome_modality"]
        cl = ClassifierWrapper(Classifier.create(
            self.accessor.accessor.accessor._controller, name,
            fs.api_resource.id(), outcome, tags=tags,
            maximum_features=maximum_features
        ), self.accessor)
        self.accessor.api_resource.update_add_classifier(
            self._controller, self.accessor.api_resource.id(),
            cl.api_resource.id()
        )
        self.api_resource.update()
        logger.info("Classifier `%s` created" % name)

        # ## compute assessment ##
        for schm in self.accessor.api_resource.schemas():
            if schm["type"] == "export":
                continue
            cl.compute_assessments(
                schm["name"], outcome_modality=outcome_modality
            )
            logger.info(
                "Classifier Evaluation Report `%s` created" % schm["name"]
            )
        ##########################

        return cl

    def clone(self, new_name=None, tags=None):
        """
        Clone the current feature set.
        """
        if not new_name:
            now = datetime.now().strftime('%Y%m%d-%H:%M:%S')
            new_name = "FeatureSet-" + now
        if not tags:
            tags = self.api_resource.tags()
        return FeatureSetWrapper(
            FeatureSet.clone(
                self._controller, self.api_resource.id(), new_name, tags=tags
            ),
            self.accessor
        )

    @should_be_terminated
    def save(self, force=False, clone=True):
        """
        Save all the modifications (change variables type, set unused, *etc*.)

        .. warning:: If ``clone = False`` the method overrides the current
            feature set resource

        :raise Exception: if ``clone = False`` and the current feature set is
            the default one.
        """
        if not clone and self == self.accessor.accessor.default_feature_set() \
                and not force:
            raise Exception(
                "The default feature set cannot be overwrite! " +
                "You have to clone it"
            )

        fs = self.clone() if clone else self
        fs.wait_until_terminated()
        self.api_resource.make_changes(
            self._controller,
            fs.api_resource.id(), *[
                {
                    "variable_ids":
                        [fs._frames[frame]._variables[k[0]]["id"]],
                    "variable_names":
                        [fs._frames[frame]._variables[k[0]]["name"]],
                    "attribute": k[1],
                    "value": self._frames[frame]._variables[k[0]][k[1]]
                }
                for frame in self._frames.keys()
                for k in self._frames[frame]._modifications.keys()
            ]
        )
        fs.update()
        return fs

    @should_be_terminated
    def is_modified(self):
        """
        Indicates if the current feature set has been modified
        """
        for frame in self._frames.values():
            if frame.is_modified():
                return True
        return False

    class _Frame:

        def __init__(self, dataset, change_type, fs):
            self._change_type = change_type
            self._dataset = dataset
            self._id_to_name = {}
            self._fs = fs
            self._variables = {}
            self._modifications = {}

        def __repr__(self):
            return self._dataset["tablename"]

        def is_modified(self):
            """
            Indicates if the frame has been modified
            """
            return len(self._modifications) > 0

        def _id(self, name):
            return self._variables[name]["id"]

        def dataset_resource(self):
            if not hasattr(self, "_dataset_resource"):
                self._dataset_resource = Dataset.retrieve(
                    self._fs._controller, self._dataset["id"]
                )
                self._modalities = {
                    mod["variable_name"]: mod
                    for mod in self._dataset_resource.modalities()
                }
            return self._dataset_resource

        def modalities(self, name):
            """
            List modalities of the feature ``name``

            :param name: feature name
            """
            assert(
                name in self._variables.keys()
            ), "Feature `%s` is not contained in frame"
            ds = self.dataset_resource()
            if name not in self._modalities.keys():
                ds.retrieve_modalities(ds._controller, ds.id(), name)
                wait = waiter()
                while not self._dataset_resource.is_terminated():
                    wait.next()
                    self._dataset_resource.update()
                self._modalities[name] = filter(
                    lambda mod: mod["variable_name"] == name,
                    self._dataset_resource.modalities()
                )[0]
            return list(self._modalities[name]["modalities"])

        def features(self, filt=lambda feat: True, id=False):
            """
            List features of the current frame

            ::

                >>> fs.features()
                [
                    {
                        'name': 'Flag_Prospect',
                        'type': 'categorical',
                        'use': True
                    },
                    {
                        'name': 'LABEL',
                        'type': 'continuous',
                        'use': True
                    },
                    ...
                ]

            :param filt: (*optional*) a function that can be used to filter
                features

            ::

                >>> fs.features(filter=lambda feat: fs.is_categorical(feat))
                [
                    {
                        'name': 'Flag_Prospect',
                        'type': 'categorical',
                        'use': True
                    },
                    ...
                ]

            or::

                >>> fs.features(filter=lambda feat: feat["name"].startswith("Foo"))
                [
                    {
                        'name': 'FooBar',
                        'type': 'categorical',
                        'use': True
                    },
                    {
                        'name': 'FooFoo',
                        'type': 'continuous',
                        'use': False
                    },
                    ...
                ]
            """
            if self.is_central() and self._fs._is_linked_to_classifier:
                li = [
                    dict(
                        (dict(
                            self._fs._classifier.feature(var["name"])
                        ).items() + [("use", var["use"])])
                        if self._fs._classifier.weight(var["name"]) > 0 else
                        ([
                            ("name", var["name"]),
                            ("type", var["type"]),
                            ("use",  var["use"])
                        ] + ([("id", var["id"])] if id else []))
                    )
                    for var in self._variables.values()
                ]
            else:
                li = [
                    {
                        "name": var["name"],
                        "type": var["type"],
                        "use":  var["use"]
                    }
                    for var in self._variables.values()
                ]

            return filter(filt, li)

        def is_central(self):
            """
            Indicates if the frame is central
            """
            return self._dataset["central"]

        def type(self, variable):
            """
            Return the type of the feature ``variable``
            The type could be ``categorical`` or ``continuous`` (other types
            can be provided like ``timestamps`` but they are not managed)

            :param variable: the feature
            """
            return self._variables[variable]["type"]

        def is_categorical(self, variable):
            """
            Indicates if the feature ``variable`` is categorical or not

            :param variable:: feature name
            """
            return self.type(variable) == "categorical"

        def is_continuous(self, variable):
            """
            Indicates if the feature ``variable`` is continuous or not

            :param variable:: feature name
            """
            return self.type(variable) == "continuous"

        def is_used(self, variable):
            """
            Return if the feature is used or not
            """
            return self._variables[variable]["use"]

        def is_change_type_allowed(self):
            """
            Indicate if the frame allows to change feature type

            It is forbidden to change type of peripheral frame features if
            there is aggregates in the central frame
            """
            return self._change_type

        def set_categorical(self, variable):
            """
            Change the type of the feature ``variable`` to categorical

            :param variable: the feature name

            :raise MangroveChangeForbidden: if change type is not allowed
            """
            if self.is_change_type_allowed():
                self._do_modification(
                    variable, "type", self._variables[variable]["type"],
                    "categorical"
                )
            else:
                raise MangroveChangeForbidden(
                    "Variable `%s` can't be changed" % variable
                )

        def set_continuous(self, variable):
            """
            Change the type of the feature ``variable`` to continuous

            :param variable: the feature name

            :raise MangroveChangeForbidden: if change type is not allowed
            """
            if self.is_change_type_allowed():
                self._do_modification(
                    variable, "type", self._variables[variable]["type"],
                    "continuous"
                )
            else:
                raise MangroveChangeForbidden(
                    "Variable `%s` can't be changed" % variable
                )

        def set_used(self, variable):
            """
            Set used the feature ``variable``

            :param variable: the feature name
            """
            self._do_modification(
                variable, "use", self._variables[variable]["use"], True
            )

        def set_unused(self, variable):
            """
            Set unused the feature ``variable``

            :param variable: the feature name
            """
            self._do_modification(
                variable, "use", self._variables[variable]["use"], False
            )

        def _do_modification(self, variable, field, old_value, new_value):
            if old_value == new_value:
                return

            if (variable, field) in self._modifications.keys():
                # if there is already a modification
                # we conserv the original value (and
                # we don't care about the "old" one)
                pass
            else:
                self._modifications[(variable, field)] = old_value
            self._variables[variable][field] = new_value
