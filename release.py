import argparse
import logging
import os
import platform
import subprocess
from enum import Enum
from typing import Optional

import run_linter
import utils


class OS(Enum):
    WINDOWS = ".exe"
    UBUNTU = ""
    MAC = ".dmg"

    def __str__(self):
        return self.name.capitalize()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--build", help="Create executable file", default=False, action="store_true")
    parser.add_argument("-t", "--title", help="Print the title of this build", default=False, action="store_true")
    parser.add_argument("-p", "--path", help="Print the executable path result", default=False, action="store_true")
    parser.add_argument("-i", "--install", help="Install all the needed packages", default=False, action="store_true")
    arguments = parser.parse_args()
    return arguments


def get_os_type() -> Optional[OS]:
    system_type = platform.system()
    if system_type == "Windows":
        return OS.WINDOWS

    if system_type == "Linux":
        return OS.UBUNTU

    if system_type == "Darwin":
        return OS.MAC

    return None


def build(os_build_type: OS):
    # pylint: disable=import-outside-toplevel
    import customtkinter

    customtkinter_path = os.path.abspath(os.path.dirname(customtkinter.__file__))
    main_path = os.path.abspath(os.path.join(utils.ROOT_PATH, "__main__.py"))
    separator = ';'
    if os_build_type in [OS.UBUNTU, OS.MAC]:
        separator = ':'

    print(f"Building executable file for {os_build_type} OS")
    print(f"Main script path: {main_path}")
    print(f"customtkinter package path: {customtkinter_path}")

    pyinstaller_cmd = f"pyinstaller --onefile --add-data {customtkinter_path}{separator}customtkinter " \
                      f"--name SemesterOrganizer{os_build_type.value} __main__.py"

    print("Running pyinstaller command: ", pyinstaller_cmd)
    return_code = subprocess.call(pyinstaller_cmd.split(" "))
    assert return_code == 0, "Pyinstaller command failed"


if __name__ == "__main__":
    utils.init_project()
    utils.config_logging_level(logging.DEBUG)
    os_type = get_os_type()
    args = get_args()
    args_count = sum([args.build, args.title, args.path])
    ERROR_MESSAGE = "Need exactly one argument from the following: build, title, path unless you just want to install."

    assert args_count == 1 or (args_count == 0 and args.install), ERROR_MESSAGE
    assert os_type, f"{os.name} OS is not supported."

    if args.install:
        run_linter.update_pip()
        run_linter.pip_install("customtkinter>=5.0.2")
        run_linter.pip_install("pyinstaller>=5.7.0")

    if args.title:
        print(f"Executable File for {os_type} OS")

    elif args.path:
        file_path = os.path.join("dist", f"SemesterOrganizer{os_type.value}")
        print(file_path)

    elif args.build:
        build(os_type)