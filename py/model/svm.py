from sklearn import svm
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from hyperparameter_evolution.hyperparameter_set import HyperparameterSet
from model.model import ClassModel, TunableClassModel
from model.model_with_coef import SKLearnModelFactoryWithExtractor, SklearnCoefExtractor, OffCoefExtractor, \
    SklearnModelWrapperWithFallback


class SVMFactory(SKLearnModelFactoryWithExtractor):

    def create(self, hyperparameters: HyperparameterSet = None):
        if hyperparameters is None:
            pipe = Pipeline([
                ('scale', StandardScaler()),
                ('svm', svm.SVC(kernel='rbf', class_weight='balanced'))])
            return pipe

        return Pipeline([('scale', StandardScaler()),('svm', svm.SVC(**hyperparameters.hyperparameters_to_kwargs()))])

    def extractor(self) -> SklearnCoefExtractor:
        return OffCoefExtractor()


class SVMWithFallback(SklearnModelWrapperWithFallback, TunableClassModel):

    def __init__(self, hyperparameters: HyperparameterSet = None):
        SklearnModelWrapperWithFallback.__init__(self, model_factory=SVMFactory(), hyperparameters=hyperparameters)

    def nick(self) -> str:
        return "svm"

    def name(self) -> str:
        return "svm"

    def tune(self, hyperparameters: HyperparameterSet) -> ClassModel:
        return SVMWithFallback(hyperparameters=hyperparameters)

    def __str__(self) -> str:
        return self.name()
