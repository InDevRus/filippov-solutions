import contextlib
import pathlib
import subprocess


def main() -> None:
    # noinspection PyPep8Naming
    TEX_FILE_DIRECTORIES: list[str] = [
        "02. Уравнения с разделяющимися переменными",
        "04. Однородные уравнения",
        "10. Уравнения, допускающие понижение порядка",
        "11. Линейные уравнения с постоянными коэффициентами",
        "12. Линейные уравнения с переменными коэффициентами",
        "15. Устойчивость",
        "16. Особые точки",
        "17. Фазовая плоскость",
        '20. Уравнения в частных производных первого порядка'
    ]
    latex_command: str = "lualatex.exe --shell-escape -synctex=1 -interaction=nonstopmode"

    for directory_name in TEX_FILE_DIRECTORIES:
        directory: pathlib.Path = pathlib.Path.cwd() / directory_name
        with contextlib.chdir(directory):
            for filepath in pathlib.Path.cwd().rglob("*.tex"):
                shell_command: str = f'{latex_command} "{filepath.name}"'

                print(f"Compiling {filepath}")
                subprocess.run(shell_command, capture_output=True)


if __name__ == '__main__':
    main()
