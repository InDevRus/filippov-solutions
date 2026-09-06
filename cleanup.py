import argparse
import itertools
import pathlib
import re
import sys
import typing
from collections.abc import Sequence

DEFAULT_CLEANUP_SOURCE: str = 'cleanup_masks.txt'
PROGRAM_NAME: str = "Скрипт очистки скомпилированных файлов."
PROGRAM_DESCRIPTION: str = "Очищает файлы с масками из файла SOURCE."

Mask = typing.NewType('Mask', str)
DAT_FILE_EXTENSION = Mask('.dat')
PDF_FILE_EXTENSION = Mask('.pdf')


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

    parser.add_argument(
        '-d', '--dat',
        action='store_true',
        help='Добавить в список расширений *.dat файлы.'
    )
    parser.add_argument(
        '-p', '--pdf',
        action='store_true',
        help='Добавить в список расширений *.pdf файлы.'
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


# noinspection PyPropertyDefinition
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

    @property
    def dat(self) -> bool:
        pass

    @property
    def pdf(self) -> bool:
        pass


EXTENSION_PATTERN = re.compile(r'\.[\w.]+')


def parse_arguments[T](parser: argparse.ArgumentParser,
                       namespace_type: type[T]) -> T:
    namespace = parser.parse_args()
    if not isinstance(namespace, namespace_type):
        print('Аргументы не соответствуют модели.', file=sys.stderr)
        sys.exit(-1)
    return namespace


def find_files_to_process(extensions_masks: Sequence[str], root: pathlib.Path | None = None) -> list[pathlib.Path]:
    current_path: pathlib.Path = pathlib.Path.cwd() if root is None else root
    target_paths = list(itertools.chain.from_iterable(
        current_path.rglob(f'*{extension_mask}') for extension_mask in extensions_masks
    ))

    target_paths.sort()
    return target_paths


def initiate_error(preamble: str, exception: Exception, exit_code: int) -> typing.Never:
    print(preamble, file=sys.stderr)
    print(exception, file=sys.stderr)
    sys.exit(exit_code)


def load_extensions_masks(source_path: str) -> list[Mask]:
    masks: list[Mask] = []

    with open(source_path, encoding='utf-8') as source_file:
        extension_mask: str
        for extension_mask in map(str.rstrip, source_file):
            if EXTENSION_PATTERN.fullmatch(extension_mask) is not None:
                masks.append(Mask(extension_mask))
                print(f'Загружены файлы расширений {extension_mask}')
    if len(masks) > 0:
        print()
    return masks


def remove_files(target_paths: Sequence[pathlib.Path], verbose: bool) -> None:
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
    arguments: ArgumentsNamespace = parse_arguments(parser, ArgumentsNamespace) # type: ignore[type-abstract]

    try:
        extensions_marks: list[Mask] = load_extensions_masks(arguments.source)
    except OSError as error:
        initiate_error(f'Не удалось открыть файл SOURCE:', error, 1)

    if arguments.dat and DAT_FILE_EXTENSION not in extensions_marks:
        extensions_marks.append(DAT_FILE_EXTENSION)
        print(f'Добавлены файлы {DAT_FILE_EXTENSION}')
        print()

    if arguments.pdf and PDF_FILE_EXTENSION not in extensions_marks:
        extensions_marks.append(PDF_FILE_EXTENSION)
        print(f'Добавлены файлы {PDF_FILE_EXTENSION}')
        print()

    try:
        target_files: Sequence[pathlib.Path] = find_files_to_process(extensions_marks)
    except OSError as error:
        initiate_error(f'Не удалось провести поиск файлов:', error, 1)

    if arguments.blank:
        for path in target_files:
            print(path)
        return

    try:
        remove_files(target_files, arguments.verbose)
    except OSError as error:
        print(f'Не удалось удалить файл:', error, 3)


if __name__ == '__main__':
    main()
