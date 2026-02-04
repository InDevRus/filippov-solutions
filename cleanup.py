import argparse
import pathlib
import sys
import typing

DEFAULT_CLEANUP_SOURCE: str = 'cleanup_masks.txt'
PROGRAM_NAME: str = "Скрипт очистки скомпилированных файлов."
PROGRAM_DESCRIPTION: str = "Очищает файлы с масками из файла SOURCE."


def prepare_argparse() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description=PROGRAM_DESCRIPTION,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-s', '--source',
        default=DEFAULT_CLEANUP_SOURCE,
        type=str,
        help=f'Источник расширений для очистки.'
    )

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        '-b', '--blank',
        action='store_true',
        help='Напечатать выбранные файлы, но не удалять их. Несовместим с -v.'
    )
    group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Печатать удаляемые файлы после удаления. Несовместим с -b.'
    )

    return parser


@typing.runtime_checkable
class ArgumentsNamespace(typing.Protocol):
    @property
    def source(self) -> str:
        pass

    @property
    def blank(self) -> bool:
        pass

    @property
    def verbose(self) -> bool:
        pass


def parse_arguments(parser: argparse.ArgumentParser) -> ArgumentsNamespace:
    namespace = parser.parse_args()
    if not isinstance(namespace, ArgumentsNamespace):
        print('Аргументы не соответствуют модели.', file=sys.stderr)
        sys.exit(-1)
    return typing.cast(ArgumentsNamespace, namespace)


def find_files_to_delete(source_path: str) -> list[pathlib.Path]:
    current_path: pathlib.Path = pathlib.Path('./')
    target_paths: list[pathlib.Path] = []

    with open(source_path, encoding='utf-8') as source_file:
        extension_mask: str
        for extension_mask in source_file:
            extension_mask = extension_mask.rstrip()
            target_paths.extend(current_path.rglob(extension_mask))

    target_paths.sort()
    return target_paths


def remove_files(target_paths: list[pathlib.Path], verbose: bool) -> None:
    path: pathlib.Path
    for path in target_paths:
        try:
            path.unlink()
        except OSError as error:
            print(f'Файл {path} удалить не получилось:', file=sys.stderr)
            print(error, file=sys.stderr)
            continue
        if verbose:
            print(f'{path} успешно удалён.')


def main() -> None:
    parser: argparse.ArgumentParser = prepare_argparse()
    arguments: ArgumentsNamespace = parse_arguments(parser)

    try:
        target_files: list[pathlib.Path] = find_files_to_delete(arguments.source)
    except OSError as error:
        print(f'Не удалось открыть файл SOURCE:', file=sys.stderr)
        print(error, file=sys.stderr)
        sys.exit(1)

    if arguments.blank:
        for path in target_files:
            print(path)
        return

    remove_files(target_files, arguments.verbose)


if __name__ == '__main__':
    main()
