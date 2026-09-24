from abstractions.i_unit_of_work import IUnitOfWork
from abstractions.i_unit_of_work_factory import IUnitOfWorkFactory
from db.database import Database
from db.unit_of_work import UnitOfWork


class UnitOfWorkFactory(IUnitOfWorkFactory):
    def __init__(self, database: Database):
        self.database = database

    def create(self) -> IUnitOfWork:
        return UnitOfWork(self.database)