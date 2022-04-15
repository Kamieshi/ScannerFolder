from __future__ import annotations

import argparse
import os
from os.path import isdir, abspath, getsize, isfile, islink
from typing import List, Optional, Tuple

parser = argparse.ArgumentParser()
parser.description = "This util will help you fast see size all your folders in directory"
parser.epilog = "Use example: $ python ScannerFolder.py --path /home/user/work"
parser.add_argument('--path', help="Path to scan directory, Default= '.'", default=".")
parser.add_argument('--sfile', help="Show files, Default FALSE", default="False")
parser.add_argument('--rl', help="Level output with projection, Default 1", default=1, type=int)
args = parser.parse_args()


class Folder:
    def __init__(self, abs_path: str, parent: Optional[Folder] = None, childes: Optional[List[Folder]] = None, level_definition: int = 0):
        self.abs_path: str = abs_path
        self.parent: Folder = parent
        self.level = self.parent.level + level_definition if self.parent else 0
        self._size: Optional[int] = None
        if childes:
            self.childes: List[Folder] = childes

    @property
    def size(self) -> int:
        if not self._size is None:
            return self._size
        folder_size = self.file_sizes()
        for child in self.childes:
            folder_size += child.size
        return folder_size

    def file_sizes(self) -> int:
        all_items: List[str] = os.listdir(self.abs_path)
        size = 0
        for item in all_items:
            if isfile(self.abs_path + "/" + item):
                size += getsize(self.abs_path + "/" + item)
        return size

    @property
    def files(self) -> List[Tuple[str, int]]:
        all_items = os.listdir(self.abs_path)
        files = [(item, getsize(self.abs_path + "/" + item)) for item in all_items if isfile(self.abs_path + "/" + item)]
        return files

    @staticmethod
    def folders(path: str) -> List[str]:
        all_items = os.listdir(path)
        dirs = [path + "/" + item for item in all_items if isdir(path + "/" + item) and not islink(path + "/" + item)]
        return dirs

    @classmethod
    def create(cls, path: str) -> Folder:
        return Folder(path)

    def init(self) -> None:
        if self.parent and self.parent.abs_path not in self.abs_path:
            print("Scan : ", "  " * self.level, self.abs_path)
        childes_dirs = Folder.folders(self.abs_path)
        childes: Optional[List[Folder]] = [Folder(dir_path, self, level_definition=1) for dir_path in childes_dirs]
        self.childes = childes
        for child in self.childes:
            child.init()

        self._size = self.size
        if self.level < 2:
            print("Scan : ", self)

    def show_tree(self, current_level: int = 0, current_prefix: str = "", max_level: int = None, show_file: bool = False) -> None:
        print(current_prefix, "-", self)

        current_prefix = current_prefix + "|" + "  "

        if show_file and current_level < max_level:
            for file, size in self.files:
                print(current_prefix, "+", file, self.to_fixed(size / (1024 ** 2), 2))

        self.childes = sorted(self.childes, key=lambda x: x.size, reverse=True)
        for child in self.childes:
            if max_level and current_level >= max_level:
                break
            child.show_tree(current_level + 1, current_prefix, max_level=max_level)

    @staticmethod
    def to_fixed(num_obj, digits=0):
        return f"{num_obj:.{digits}f}"

    def __repr__(self):

        return self.abs_path.split("/")[-1] + "  " + self.to_fixed(self.size / (1024 ** 2), 2) + " MB"


class Scanner:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.folders_tree: Folder = self.scan()

    def scan(self) -> Folder:
        main_folder = Folder.create(abspath(self.base_path))
        main_folder.init()
        return main_folder


if __name__ == '__main__':
    show_file = True if "ue" in args.sfile else False
    path = args.path
    max_level = args.rl
    scan = Scanner(path)
    scan.folders_tree.show_tree(max_level=max_level, show_file=show_file)
