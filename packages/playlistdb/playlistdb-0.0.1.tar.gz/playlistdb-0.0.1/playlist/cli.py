import argparse

from . import doc_split, usage, version
from .playlist import PlayDB


def add(files):
    """Add files in the current directory to the database.
    """
    PlayDB().add(files)


def remove(files):
    """Remove files in the current directory from the database.
    """
    PlayDB().remove(files)


def set(filename):
    """Set the current file.
    """
    PlayDB().set(filename)


def current():
    """Get the current file.
    """
    print PlayDB().current()


def next():
    """Go to the next file.
    """
    db = PlayDB()
    print db.current()
    db.next()


def show():
    """Show the database for the current directory.
    """
    PlayDB().show()


def config(config_string):
    """Set configuration for the current directory.
    """
    PlayDB().config(config_string)


def show_config():
    """Show configuration for the current directory.
    """
    PlayDB().show_config()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=usage[0], epilog=usage[1])
    parser.add_argument('-v', action='version', version=version(parser.prog))
    subparsers = parser.add_subparsers(dest='subcommand')

    subparser = subparsers.add_parser('add', help=doc_split(add))
    subparser.add_argument(
        'files', metavar='FILE', type=str, nargs='+', help='Files to add.')
    subparser.set_defaults(func=add)

    subparser = subparsers.add_parser('remove', help=doc_split(remove))
    subparser.add_argument(
        'files', metavar='FILE', type=str, nargs='+', help='Files to remove')
    subparser.set_defaults(func=remove)

    subparser = subparsers.add_parser('set', help=doc_split(set))
    subparser.add_argument(
        'filename', metavar='FILE', type=str, help='New current file.')
    subparser.set_defaults(func=set)

    subparser = subparsers.add_parser('current', help=doc_split(current))
    subparser.set_defaults(func=current)

    subparser = subparsers.add_parser('next', help=doc_split(next))
    subparser.set_defaults(func=next)

    subparser = subparsers.add_parser('show', help=doc_split(show))
    subparser.set_defaults(func=show)

    subparser = subparsers.add_parser('config', help=doc_split(config))
    subparser.add_argument(
        'config_string', metavar='CONFIG', type=str,
        help='Configuration string.')
    subparser.set_defaults(func=config)

    subparser = subparsers.add_parser(
        'show_config', help=doc_split(show_config))
    subparser.set_defaults(func=show_config)

    args = parser.parse_args()

    args.func(**{k: v for k, v in vars(args).items()
        if k not in ('func', 'subcommand')})
