from random import randint

from hyperparameter_evolution.hyperparameter import Hyperparameter


class IntegerHyperparameter(Hyperparameter):
    __lower_bound: int
    __upper_bound: int
    __mutation_range: int

    def __init__(
        self,
        nick: str,
        name: str,
        lower_bound: int,
        upper_bound: int,
        mutation_range: int | None = None,
        value: int | None = None,
        mutable: bool = True
    ):
        super().__init__(nick=nick, name=name, value=value, mutable=mutable)

        if lower_bound > upper_bound:
            raise ValueError("lower_bound debe ser mas pequeño a upper_bound")

        if mutation_range is not None and mutation_range < 0:
            raise ValueError("mutation_range debe ser mayor a 0")

        self.__lower_bound = lower_bound
        self.__upper_bound = upper_bound
        self.__mutation_range = mutation_range

    def lower_bound(self) -> int:
        return self.__lower_bound

    def upper_bound(self) -> int:
        return self.__upper_bound

    def mutation_range(self) -> int:
        return self.__mutation_range

    def random_initialize(self):
        """
        Asigna un valor integer al azar, sin salir de las cotas
        """
        if not self.mutable():
            return
        
        self.set_value(
            randint(self.lower_bound(), self.upper_bound())
        )

    def mutate(self):
        """
        Muta el valor del hiperparametro según el rango de mutación
        """
        if not self.mutable():
            return
        
        current = self.value()

        # Si todavía no tiene valor o no tiene rango de mutación, lo inicializamos
        if current is None or self.mutation_range() is None:
            self.random_initialize()
            return

        displacement = randint(-self.mutation_range(), self.mutation_range())

        new_value = current + displacement

        # Respetar límites
        new_value = max(self.lower_bound(), new_value)
        new_value = min(self.upper_bound(), new_value)

        self.set_value(new_value)