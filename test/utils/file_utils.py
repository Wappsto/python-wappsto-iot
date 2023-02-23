import pathlib


def rm_all(folder: pathlib.Path) -> None:
    if folder.is_dir():
        for item in folder.iterdir():
            rm_all(item)
        folder.rmdir()
        return

    if folder.is_file() or folder.is_symlink():
        folder.unlink()
