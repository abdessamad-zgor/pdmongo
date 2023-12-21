from shell.core import Shell, get_command_line_args, get_client
from shell.scope import ShellScope

def main():
    args = get_command_line_args()
    client = get_client(args.url)
    shell_scope = ShellScope(client, client['test'])
    shell = Shell(shell_scope)
    shell.run_repl()
    

if __name__ == "__main__":
    main()
