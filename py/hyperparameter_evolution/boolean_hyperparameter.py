from random import choice

from hyperparameter_evolution.hyperparameter import Hyperparameter


class BooleanHyperparameter(Hyperparameter):

    def __init__(
        self,
        nick: str,
        name: str,
        value: bool | None = None,
        mutable: bool = True
    ):
        super().__init__(nick=nick, name=name, value=value, mutable=mutable)

    def random_initialize(self):
        """
        Asigna un valor booleano al azar.
        """
        if not self.mutable():
            return
        
        self.set_value(
            choice([True, False])
        )

    def mutate(self):
        """
        Invierte el valor del hiperparámetro.
        """
        if not self.mutable():
            return
        
        current = self.value()

        # Si todavía no tiene valor, lo inicializamos
        if current is None:
            self.random_initialize()
            return

        self.set_value(not current)