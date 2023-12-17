from pymongo import MongoClient
from pymongo.database import Database


class ShellScope:
    def __init__(self, client: MongoClient, db: Database, locals: dict = {}) -> None:
        self.client = client
        self.db = db
        self.locals = locals

    def to_dict(self):
        scope_dict = {key: value for key, value in vars(self).items() if not callable(value)}
        return scope_dict
    @staticmethod
    def from_dict(obj):
        return ShellScope(obj['client'], obj['db'], obj['locals'])
        
