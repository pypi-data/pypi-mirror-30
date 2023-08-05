import pkg_resources
import argparse

def main():
    parser = argparse.ArgumentParser(prog='pkit')
    sp = parser.add_subparsers()

    for entry in pkg_resources.iter_entry_points(group='pkit.commands'):
        entry_mod = entry.load()
        entry_parser = sp.add_parser(entry.name)
        entry_parser.set_defaults(func=entry_mod.run)

        if hasattr(entry_mod, 'parse'):
            entry_mod.parse(entry_parser)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        kwargs = vars(args)
        func = kwargs.pop('func')
        return func(**kwargs)
    else:
        parser.print_usage()

if __name__ == '__main__':
    main()