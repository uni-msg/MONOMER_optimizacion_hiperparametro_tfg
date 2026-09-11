from sklearn.ensemble import RandomForestClassifier
from hyperparameter_evolution.hyperparameter_set import HyperparameterSet
from model.model import ClassModel, TunableClassModel
from model.model_with_coef import SklearnModelWrapperWithFallback, SKLearnModelFactoryWithExtractor, \
    SklearnCoefExtractor, OffCoefExtractor


class ForestFactory(SKLearnModelFactoryWithExtractor):

    def create(self, hyperparameters: HyperparameterSet = None):
        if hyperparameters is None:
            return RandomForestClassifier(class_weight="balanced", n_estimators=30, min_samples_leaf=2, n_jobs=1)
        return RandomForestClassifier(**hyperparameters.hyperparameters_to_kwargs())

    def extractor(self) -> SklearnCoefExtractor:
        return OffCoefExtractor()


class ForestWithFallback(SklearnModelWrapperWithFallback, TunableClassModel):

    def __init__(self, hyperparameters: HyperparameterSet = None):
        SklearnModelWrapperWithFallback.__init__(self, model_factory=ForestFactory(), hyperparameters=hyperparameters)

    def nick(self) -> str:
        return "RF"

    def name(self) -> str:
        return "random forest"

    def tune(self, hyperparameters: HyperparameterSet) -> ClassModel:
        return ForestWithFallback(hyperparameters=hyperparameters)

    def __str__(self) -> str:
        return self.name()
