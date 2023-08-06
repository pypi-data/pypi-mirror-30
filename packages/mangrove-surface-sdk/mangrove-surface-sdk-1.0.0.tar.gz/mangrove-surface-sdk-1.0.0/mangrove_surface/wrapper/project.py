from datetime import datetime
from dateutil import parser
from mangrove_surface.api.collection import Collection
from mangrove_surface.wrapper import Wrapper
from mangrove_surface.wrapper.collection import CollectionWrapper
from mangrove_surface.wrapper.feature_set import FeatureSetWrapper
from mangrove_surface.api.feature_set import FeatureSet
from mangrove_surface.wrapper.classifier import ClassifierWrapper
from mangrove_surface.api.classifier import Classifier
import warnings


class ClassifierDoesNotExist(KeyError):
    pass


class CollectionDoesNotExist(KeyError):
    pass


class ProjectWrapper(Wrapper):
    """
    Project resource
    """

    def __init__(self, project_resource, mang):
        Wrapper.__init__(self, project_resource, mang)

    def delete(self):
        for coll in self.collections():
            for schm in coll.schemas():
                for fs in schm.feature_sets():
                    fs.delete()
                for ds in schm.datasets():
                    ds.delete()
        super(ProjectWrapper, self).delete()

    def create_collection(self):
        """
        Create a new collection

        A collection stores similar schemas of data sets.

        .. warning::

            Expert method: it should be only use to store new data set schemas
        """
        now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
        coll = Collection.create(
            self._controller, self.api_resource.id(),
            "Collection-" + now, ""
        )
        return CollectionWrapper(coll, self)

    def default_feature_set(self):
        """
        Return the default feature set

        (see: :mod:`mangrove.wrapper.feature_set`)
        """
        coll = self.collections()[-1]
        fss = sorted(
            list(map(
                lambda id: FeatureSet.retrieve(self._controller, id),
                coll._schema()["feature_set_ids"]
            )),
            key=lambda fs: parser.parse(fs.created_at())
        )
        return FeatureSetWrapper(fss[0], coll)

    def collections(self):
        """
        List all collections
        """
        return [CollectionWrapper(coll, self)
                for coll in Collection.retrieve_all(
                    self._controller, project_id=self.api_resource.id())
                ]

    def collection(self, name):
        """
        Return the collection named ``name``

        :param name: collection name

        """
        cls = list(
            filter(lambda coll: coll.name() == name, self.collections())
        )
        if len(cls) == 0:
            raise CollectionDoesNotExist(name + ' does not exists')

        return cls[0]

    def schemas(self, type=None):
        """
        List all schemas

        :param type: (*optional*) ``type`` could be ``train``, ``test`` or
            ``export``. It is to filter schemas of type ``type``. By default
            all schemas are listed.

        """
        if type:
            return [schm
                    for coll in self.collections()
                    for schm in coll.schemas()
                    if schm.type() == type]
        return [schm
                for coll in self.collections()
                for schm in coll.schemas()]

    def classifiers(self):
        """
        List all classifiers

        ::

            >>> pj.classifiers()
            [
                Project_2018-03-20T15:39:18.120Z,
                Project_2018-03-20T15:40:02.880Z,
                Project_2018-03-20T15:40:45.242Z,
                MyClassifier
            ]

        """
        return [
            ClassifierWrapper(
                Classifier.retrieve(self._controller, cl_id), coll
            )
            for coll in self.collections()
            for cl_id in coll.api_resource.classifier_ids()
        ]

    def classifier(self, name):
        """
        Return classifier named ``name``

        :param name: project name
        :raise ClassifierDoesNotExist: if there is no classifier named ``name``

        """
        cls = list(filter(lambda cl: cl.name() == name, self.classifiers()))
        if len(cls) == 0:
            raise ClassifierDoesNotExist(name + ' does not exists')
        elif len(cls) > 1:
            warnings.warn("There is several classifier called `%s`! " % name +
                          "The 1st has been selected.")
        return cls[0]

    def description(self):
        """
        Project description
        """
        return self.api_resource.description()

    def update_description(self, new_description):
        """
        Update the project description

        :param new_description: the new project description
        """
        self.api_resource.update_description(
            self._controller,
            self.api_resource.id(),
            new_description
        )
        self.update()

    def update_name(self, new_name):
        """
        Update the project name

        :param new_name: the new project name
        """
        self.api_resource.rename(
            self._controller,
            self.api_resource.id(),
            new_name
        )
        self.update()

    def tags(self):
        """
        Return the project tags
        """
        return list(self.api_resource.tags())

    def update_tags(self, new_tags=[]):
        """
        Update the project tags

        :param new_tags: the list of new tags
        """
        self.api_resource.rename(
            self._controller,
            self.api_resource.id(),
            tags=new_tags
        )
        self.update()
