import re
import os
from biro.middleware import Error
from biro.loader import Loader
import typing as t


class Preprocessor:
    """Preprocess the code, installs the dependencies and add the other code into the file"""

    def __init__(self, file: str, libpath: str, pirocode: str) -> None:
        """
        Constructor method

        :param file: file path to preprocess
        :type file: str
        :param libpath: path of the `lib` directory
        :type libpath: str
        :param pirocode: name of the intermediate preprocessed file
        :type pirocode: str
        """
        self.file = os.path.abspath(file)
        self.deps = []
        self.pirocode = pirocode
        self.libpath = libpath

    def resolve_directives(self, file):
        with open(file, "r") as f:
            for line in f:
                line = line.strip()
                if not re.match("^!.*", line):
                    break
                line = line[1:].strip().split(" ")
                cmd = line[0]
                args = " ".join(line[1:]).strip()
                if cmd == "install" and (cmd, args) not in self.deps:
                    self._install(args)
                elif cmd == "add":
                    dirname = os.path.dirname(self.file)
                    filename = os.path.abspath(os.path.join(dirname, args))
                    if not os.path.exists(filename) or not os.path.isfile(
                        filename
                    ):
                        module = os.path.abspath(
                            os.path.join(self.libpath, args)
                        )
                        if not os.path.exists(module) or not os.path.isfile(
                            module
                        ):
                            Error().show(
                                f"Error reading file {filename} or {module}."
                            )
                            exit(1)
                        filename = module
                    self.resolve_directives(filename)
                    args = filename
                if (cmd, args) not in self.deps:
                    self.deps.append((cmd, args))

    def process(self):
        self.resolve_directives(self.file)
        print(self.deps)
        open(self.pirocode, "w").close()
        for deps in self.deps:
            if deps[0] == "add":
                self._add_dep_file(deps[1])

        self._add_dep_file(self.file)

    def _install(self, pkg):
        ldr = Loader(
            f"Installing {pkg} ",
            f"[o] Installed {pkg}",
            0.1,
            " ",
            "  ",
        )
        ldr.start()
        try:
            # TODO: Installation code
            ldr.stop()
        except:
            ldr.end = f"[x] Failed to install {pkg}"
            ldr.stop()
            exit(1)

    def _add_dep_file(self, dep_file):
        with open(dep_file) as p, open(self.pirocode, "a") as f:
            for line in p:
                if not line.lstrip().startswith("!"):
                    f.write(line)
            f.write("\n")
