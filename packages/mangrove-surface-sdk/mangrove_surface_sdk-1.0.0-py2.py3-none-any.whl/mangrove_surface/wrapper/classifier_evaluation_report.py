from mangrove_surface.wrapper import Wrapper, run_once, should_be_terminated


class ClassifierEvaluationReportWrapper(Wrapper):
    """
    Classifier Evaluation Report resource
    """

    def __init__(self, classifier_evaluation_report, classifier):
        Wrapper.__init__(self, classifier_evaluation_report, classifier)
        from mangrove_surface.wrapper.feature_set import FeatureSetWrapper
        from mangrove_surface.api.feature_set import FeatureSet
        collection = classifier.accessor
        self.feature_set = FeatureSetWrapper(
            FeatureSet.retrieve(
                self._controller, self.api_resource.feature_set_id()
            ),
            collection
        )

    def name(self):
        return ("Evaluation Report of model `%s` focus on modality `%s` " +
                "over schema `%s`") % (
            self.accessor.name(), self.api_resource.outcome_modality(),
            self.feature_set.name()
        )

    @should_be_terminated
    def confusion_matrix(self):
        """
        Confusion matrix

        ::
            >>> ass.confusion_matrix()
            {
                'matrix': [
                    [13376, 1393],
                    [  683, 4084]
                ],
                'modalities': ['N', 'Y']
            }

        """
        return self.api_resource.confusion_matrix()

    def instances(self, outcome_modality=None):
        """
        Number of instances evaluated
        """
        matrix = self.confusion_matrix()["matrix"]
        n = len(matrix)
        if not outcome_modality:
            return sum(matrix[i][j] for i in range(n) for j in range(n))
        pos = self.confusion_matrix()["modalities"].index(outcome_modality)
        return sum(matrix[pos][i] for i in range(n))

    def target_rate(self, outcome_modality):
        """
        Target rate of the modality ``outcome_modality``

        :param outcome_modality: a modality
        """
        mat_conf = self.confusion_matrix()
        pos = mat_conf['modalities'].index(outcome_modality)
        return float(sum(map(
            lambda l: l[pos],
            mat_conf['matrix']
        ))) / self.instances()

    def true_positive(self, outcome_modality=None):
        """
        Number of correct predictions

        True positive = correctly identified

        :param outcome_modality: (*optional*) compute the number of correct
            prediction associated to this modality

        :raise KeyError: if the ``outcome_modality`` does not exist

        ::

            >>> ass.true_positive()
            17460

            >>> ass.true_positive('Y')
            4084

        """
        matrix = self.confusion_matrix()["matrix"]
        if not outcome_modality:
            n = len(matrix)
            return sum(matrix[i][i] for i in range(n))
        pos = self.confusion_matrix()["modalities"].index(outcome_modality)
        return matrix[pos][pos]

    def false_positive(self, outcome_modality=None):
        """
        Number of incorrect predictions

        False positive = incorrectly identified

        :param outcome_modality: (*optional*) compute the number of incorrect
            prediction associated to this modality

        :raise KeyError: if the ``outcome_modality`` does not exist

        ::

            >>> ass.false_positive()
            2076

            >>> ass.false_positive('Y')
            4084

        """
        matrix = self.confusion_matrix()["matrix"]
        n = len(matrix)
        if not outcome_modality:
            return sum(
                matrix[i][j]
                for i in range(n)
                for j in range(n) if j != i
            )
        pos = self.confusion_matrix()["modalities"].index(outcome_modality)
        return sum(matrix[i][pos] for i in range(n) if i != pos)

    def false_negative(self, outcome_modality):
        """
        Number of false negative errors of the ``outcome_modality``

        False negative = incorrectly rejected

        :param outcome_modality: (*optional*) compute the number of incorrect
            rejection of the modality

        """
        matrix = self.confusion_matrix()["matrix"]
        n = len(matrix)
        pos = self.confusion_matrix()["modalities"].index(outcome_modality)
        return sum(
            matrix[i][pos]
            for i in range(n) if i != pos
        )

    def true_negative(self, outcome_modality):
        """
        Number of true negative errors of the ``outcome_modality``

        True negative = correctly rejected

        :param outcome_modality: (*optional*) compute the number of correct
            rejection of the modality
        """
        matrix = self.confusion_matrix()["matrix"]
        n = len(matrix)
        pos = self.confusion_matrix()["modalities"].index(outcome_modality)
        return sum(
            matrix[i][j]
            for i in range(n) if i != pos
            for j in range(n) if j != pos
        )

    def true_positive_rate(self, outcome_modality=None):
        """
        True positive rate

        :param outcome_modality: (*optional*) the modality

        .. note::
            This method has some alias:
             - ``recall``
             - ``TPR``
             - ``sensitivity``
             - ``probability_of_detection``

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return float(self.true_positive(outcome_modality=outcome_modality)) / (
            self.true_positive(outcome_modality=outcome_modality) +
            self.false_positive(outcome_modality=outcome_modality)
        )
    TPR = true_positive_rate
    recall = true_positive_rate
    sensitivity = true_positive_rate
    probability_of_detection = true_positive_rate

    def false_positive_rate(self, outcome_modality=None):
        """
        False positive rate

        :param outcome_modality: (*optional*) the modality

        .. note::
            This method has some alias:
             - ``FPR``
             - ``fall_out``

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return (
            float(self.false_positive(outcome_modality=outcome_modality)) /
            (
                self.false_positive(outcome_modality=outcome_modality) +
                self.true_negative(outcome_modality=outcome_modality)
            )
        )
    FPR = false_positive_rate
    fall_out = false_positive_rate

    def false_negative_rate(self, outcome_modality=None):
        """
        False negative rate

        :param outcome_modality: (*optional*) the modality

        .. note::
            This method has some alias:
             - ``FNR``
             - ``miss_rate``

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return 1. - self.true_positive_rate(outcome_modality=outcome_modality)
    FNR = false_negative_rate
    miss_rate = false_negative_rate

    def true_negative_rate(self, outcome_modality=None):
        """
        True negative rate

        :param outcome_modality: (*optional*) the modality

        .. note::
            This method has some alias:
             - ``TNR``
             - ``specificity``
             - ``SPC``

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return 1. - self.false_negative_rate(outcome_modality=outcome_modality)
    TNR = true_negative_rate
    specificity = true_negative_rate
    SPC = true_negative_rate

    def positive_likehood_ratio(self):
        """
        Positive Likehood ratio

        .. note::
            This method has some alias:
             - ``LRp``

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return self.true_positive_rate() / self.false_positive_rate()
    LRp = positive_likehood_ratio

    def negative_likehood_ratio(self):
        """
        Negative Likehood ratio

        .. note::
            This method has some alias:
             - ``LRp``

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return self.false_negative_rate() / self.true_negative_rate()
    LRm = negative_likehood_ratio

    def prevalence(self):
        """
        Prevalence

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return self.true_positive() / float(self.instances())

    def precision(self, outcome_modality=None):
        """
        Precision

        :param outcome_modality: (*optional*) the modality

        .. note::
            This method has some alias:
             - ``positive_predictive_value``

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return self.true_positive(outcome_modality) / \
            float(self.instances(outcome_modality))
    positive_predictive_value = precision
    PPV = precision

    def false_omission_rate(self, outcome_modality):
        """
        False omission rate

        :param outcome_modality: (*optional*) the modality

        .. note::
            This method has some alias:
             - ``FOR``

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return self.false_negative(outcome_modality) / \
            float(self.false_negative())
    FOR = false_omission_rate

    def accuracy(self):
        """
        Accuracy

        .. note::
            This method has some alias:
             - ``ACC``

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return float(self.true_positive()) / self.instances()
    ACC = accuracy

    def false_discovery_rate(self, outcome_modality):
        """
        False discovery rate

        :param outcome_modality: (*optional*) the modality

        .. note::
            This method has some alias:
             - ``FDR``

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        matrix = self.confusion_matrix()["matrix"]
        n = len(matrix)
        pos = self.confusion_matrix()["modalities"].index(outcome_modality)
        acc = sum(matrix[i][pos] for i in range(n))
        return self.false_positive(outcome_modality) / float(acc)

        # TODO
        raise NotImplementedError()
    FDR = false_discovery_rate

    def negative_predictive_value(self, outcome_modality):
        """
        Negative predictive value

        :param outcome_modality: (*optional*) the modality

        .. note::
            This method has some alias:
             - ``NPV``

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return self.true_negative(outcome_modality) / \
            float(self.false_negative())
    NPV = negative_predictive_value

    def diagnostic_odds_ratio(self):
        """
        Diagnostic odds ratio

        .. note::
            This method has some alias:
             - ``DOR``

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return self.positive_likehood_ratio() / self.negative_likehood_ratio()
    DOR = diagnostic_odds_ratio

    def F1_score(self, outcome_modality=None):
        """
        F1 score

        :param outcome_modality: (*optional*) the modality

        .. see: https://en.wikipedia.org/wiki/Precision_and_recall
        """
        return 2. / (
            1. / self.recall(outcome_modality) +
            1. / self.precision(outcome_modality)
        )

    @should_be_terminated
    def area_under_curve(self):
        """
        Area under curve
        """
        return self.api_resource.area_under_curve()
    auc = area_under_curve
    AUC = area_under_curve

    def gini(self):
        """
        Gini coefficient
        """
        return 2 * self.area_under_curve() - 1

    @should_be_terminated
    def lift_curve(self, using="classifier"):
        """
        Lift curve over the schema

        :param using: is ``classifier`` or ``optimal``; by default the lift
            curve associated to the classifier.
        """
        return self.api_resource.lift_curves()[using]
