import argparse
import itertools
import pathlib
import sys


def parse_arguments[T](parser: argparse.ArgumentParser,
                       namespace_type: type[T]) -> T:
    namespace = parser.parse_args()
    if not isinstance(namespace, namespace_type):
        print('Аргументы не соответствуют модели.', file=sys.stderr)
        sys.exit(-1)
    return namespace


def find_files_to_process(extensions_masks: list[str]) -> list[pathlib.Path]:
    current_path: pathlib.Path = pathlib.Path.cwd()
    target_paths = list(itertools.chain.from_iterable(
        current_path.rglob(f'*{extension_mask}') for extension_mask in extensions_masks
    ))

    target_paths.sort()
    return target_paths


def initiate_error(preamble: str, exception: Exception, exit_code: int) -> typing.Never:
    print(preamble, file=sys.stderr)
    print(exception, file=sys.stderr)
    sys.exit(exit_code)