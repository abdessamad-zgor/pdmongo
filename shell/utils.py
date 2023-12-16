import pandas as pd
from typing import List
from .scope import ShellScope

class Builtin:

    @staticmethod
    def use(scope: ShellScope, name: str):
        scope_dict = scope.to_dict()
        scope_dict['db'] = scope_dict['client'][name]
        return (ShellScope.from_dict(scope_dict), f"> switched database to '{name}'")

    @staticmethod
    def load_json(scope: ShellScope, collection: str, path: str):
        df = pd.read_json(path, orient='records')
        scope_dict = scope.to_dict()
        scope_dict['locals']['df'] = df
        scope_dict['db'][collection].insert_many(df.to_json(orient='records'))

        return (ShellScope.from_dict(scope_dict), f"loaded file '{path}' to collection '{collection}'")

    @staticmethod
    def load_csv(scope: ShellScope, collection: str, path:str, cols: List[str]= []):
        df = pd.read_csv(path, orient='records', names=cols)
        scope_dict = scope.to_dict()
        scope_dict['locals']['df'] = df
        scope_dict['db'][collection].insert_many(df.to_json(orient='records'))

        return (ShellScope.from_dict(scope_dict),f"loaded file '{path}' to collection '{collection}'")
