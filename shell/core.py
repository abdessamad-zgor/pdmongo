import argparse
import ast
import inspect

from .utils import Builtin
from .scope import ShellScope
from contextlib import redirect_stdout
from io import StringIO
from pymongo import MongoClient

# Firstly, get the arguments provided by the user 
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type=str, default='mongodb://localhost', help='url to MongoDb instance if none then localhost is used by default.')
    #parser.add_argument()
    args = parser.parse_args()

    return args

# Gets MongoDB Client using `pymongo`
def get_client(url: str):
    client = MongoClient(url)
    return client

# detects if input calls builtin functions
def is_shell_builtin(input: str):
    command_tree = ast.parse(input)
    command_node = command_tree.body[0]
    builtin_funcs = {name: obj for name, obj in inspect.getmembers(Builtin) if not name.startswith('__')}
    print(builtin_funcs)
    print(ast.dump(command_node))
    if (isinstance(command_node, ast.Expr) and
        isinstance(command_node.value, ast.Call) and
        isinstance(command_node.value.func, ast.Name) and
        hasattr(command_node.value.func, 'id') and
            command_node.value.func.id in builtin_funcs):
        arguments = command_node.value.args[0].value
        return (builtin_funcs[command_node.value.func.id], [arguments])
    return None

def oexec(scope: ShellScope, input: str):
    buffer = StringIO()
    scope_dict = scope.to_dict()
    locals = {}
    with redirect_stdout(buffer):
        exec(input, scope_dict, locals)
    output = buffer.getvalue()
    scope_dict['locals'].update(locals)
    return (ShellScope.from_dict(scope_dict), output)

# A Shell makes the connection to database and allows the user to execute commands 
# and use the client API remotely with feedback
class Shell:
    def __init__(self, scope: ShellScope):
        self.scope = scope

    def run_repl(self):
        while True:
            try:
                command = input(f"{self.scope.db.name}> ")
                (scope, output) = self.run_command(command)
                print(output)
                self.scope = scope
            except Exception as e:
                raise e
    
    def run_command(self, input: str):
        result = is_shell_builtin(input)
        print(result)
        if result:
            return result[0](self.scope, *result[1])
        else:
            return oexec(self.scope, input)
