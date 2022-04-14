import random
from configargparse import ArgumentParser
from .utils.configarg import get_args
from .about import __version__, __desp__


def preprocess_args(args):
    if hasattr(args, 'seed'):
        random.seed(args.seed)
        print(f"set seed: {args.seed}")
    if hasattr(args, 'freestream_angle'):
        assert len(args.freestream_angle) == 2
        print(f'set freestream angle range [{args.freestream_angle[0]} , {args.freestream_angle[1]}]')
    if hasattr(args, 'freestream_length'):
        assert len(args.freestream_length) == 2
        print(f'set freestream length range [{args.freestream_length[0]}, {args.freestream_length[1]}]')

def handle_generate(args):
    from .generate import generate_from_cli
    preprocess_args(args)
    generate_from_cli(args)


def main():
    parser = ArgumentParser(
        description=__desp__,
    )
    parser.add_argument(
            '-V',
            '--version',
            action='version',
            version=f'airfoil-generator version: {__version__}'
    )
    subparsers = parser.add_subparsers(title='commands')

    # handle generate data
    generate_parser = subparsers.add_parser(
            'generate', help='generate flow field data'
    )
    generate_parser = get_args(generate_parser)
    generate_parser.set_defaults(
            handle=handle_generate, parser=generate_parser
    )

    args, _ = parser.parse_known_args()

    if hasattr(args, 'handle'):
        args.handle(args)


if __name__ == '__main__':
    main()
