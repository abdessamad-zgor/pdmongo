import sys
import argparse
import ast
import inspect
from typing import Any

from .utils import Builtin
from .scope import ShellScope
from contextlib import redirect_stdout
from io import StringIO
from pprint import pprint
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

# return true if input is a string representation of an expression else false 
def is_expression(input: str, scope: ShellScope):
    try:
        buffer = StringIO()
        scope_dict = scope.to_dict()
        locals_dict = scope_dict['locals']
        result = ''
        with redirect_stdout(buffer):
            result = eval(input, scope_dict, locals_dict)
        return True if result else False
    except Exception as e:
        return False

# detects if input calls builtin functions
def is_shell_builtin(input: str):
    command_tree = ast.parse(input)
    command_node = command_tree.body[0]
    builtin_funcs = {name: obj for name, obj in inspect.getmembers(Builtin) if not name.startswith('__')}
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
    locals = scope_dict['locals']
    with redirect_stdout(buffer):
        exec(input, scope_dict, locals)
    output = buffer.getvalue()
    scope_dict['locals'].update(locals)
    return (ShellScope.from_dict(scope_dict), output)

def repr_output(value: Any):
    def is_iter(val: Any):
        try:
            iter(val)
            return True
        except Exception as e:
            return False
    if is_iter(value) and not isinstance(value, str):
        return dict(value) if isinstance(value, dict) else list(value)
    return value

def pdprint(value: Any):
    value = repr_output(value)
    if isinstance(value, str):
        print(value)
    else:
        pprint(value)

        


# A Shell makes the connection to database and allows the user to execute commands 
# and use the client API remotely with feedback
class Shell:
    def __init__(self, scope: ShellScope):
        self.scope = scope

    def run_repl(self):
        print(f"Welcome to PdMongo the Mongo shell you need!\nMongoDB f{self.scope.client.server_info()['version']}; Python {sys.version}")
        while True:
            try:
                command = input(f"{self.scope.db.name}> ")
                (scope, output) = self.run_command(command)
                pdprint(output)
                self.scope = scope
            except Exception as e:
                raise e
    
    def run_command(self, input: str):
        result = is_shell_builtin(input)
        if result:
            return result[0](self.scope, *result[1])
        else:
            if is_expression(input, self.scope):
                scope_dict = self.scope.to_dict()
                locals_dict = scope_dict['locals']
                result = eval(input, scope_dict, locals_dict)
                scope_dict['locals'].update(locals_dict)
                return (ShellScope.from_dict(scope_dict), result)
            else:
                return oexec(self.scope, input)
