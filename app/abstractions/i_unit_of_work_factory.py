from abc import ABC, abstractmethod

from abstractions.i_unit_of_work import IUnitOfWork


class IUnitOfWorkFactory(ABC):
    @abstractmethod
    def create(self) -> IUnitOfWork:
        pass
