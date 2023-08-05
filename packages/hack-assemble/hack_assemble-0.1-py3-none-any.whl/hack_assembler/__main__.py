import os
import sys
from .assemble import assemble


def main(source_code_file=None):
    """ Writes a .hack file, containing a Hack machine language command per line.

    Args:
        source_code_file: a path to a Hack assembly file.

    """

    if not source_code_file:
        source_code_file = os.path.join(os.curdir, sys.argv[1])

    hack_file = f"{os.path.splitext(source_code_file)[0]}.hack"

    with open(hack_file, "w") as f:
        for line in assemble(source_code_file)["assembled"]:
            f.write(f"{line}\n")


if __name__ == "__main__":
    main()
