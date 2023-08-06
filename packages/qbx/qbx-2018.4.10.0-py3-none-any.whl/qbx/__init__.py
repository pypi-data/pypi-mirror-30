import logging
import sys

from .uproxy import uproxy
from .haproxy import haproxy
from .pull import pull
from .watchgit import watch_git, watch_git_http
from .auth_wrapper import auth_wrapper

help_doc = """
usage: qbx [--help] 
           <command> [<args>]

These are some qbx commands:
    auth_wrapper
    register_kong
    register_ws
    watch_git
    watch_git_http
    pull
    haproxy
    uproxy
"""


def print_help():
    print(help_doc)


def run():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    print('argv---', sys.argv)
    if len(sys.argv) == 1:
        print_help()
    else:
        if sys.argv[1] == 'register_kong':
            from .register_kong import register_kong
            register_kong(sys.argv[2:])
        elif sys.argv[1] == 'register_ws':
            from .register_ws import register_ws
            register_ws(sys.argv[2:])
        elif sys.argv[1] == 'watch_git':
            watch_git(sys.argv[2:])
        elif sys.argv[1] == 'watch_git_http':
            watch_git_http(sys.argv[2:])
        elif sys.argv[1] == 'haproxy':
            haproxy(sys.argv[2:])
        elif sys.argv[1] == 'pull':
            pull(sys.argv[2:])
        elif sys.argv[1] == 'uproxy':
            uproxy(sys.argv[2:])
        elif sys.argv[1] == 'auth_wrapper':
            auth_wrapper(sys.argv[2:])
        else:
            if sys.argv[1] != 'help' and sys.argv[1] != '--help':
                logging.warning('method not regognize')
            print_help()


if __name__ == '__main__':
    watch_git(['git+ssh://git@github.com/qbtrade/quantlib.git', 'log_rpc.py'])
