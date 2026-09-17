from db.database import Database
from db.unit_of_work import UnitOfWork

class UnitOfWorkFactory:
    def __init__(self, database : Database):
        self.database = database

    def create(self)->UnitOfWork:
        return UnitOfWork(self.database)