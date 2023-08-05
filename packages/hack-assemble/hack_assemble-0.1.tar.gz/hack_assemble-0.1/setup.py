import sys
from setuptools import setup
from setuptools.command.test import test as test_command


with open("README.rst") as f:
    long_description = f.read()


classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Topic :: Software Development :: Assemblers"
] + [
    ("Programming Language :: Python :: %s" % x)
    for x in "3.6 3.7".split()
]


class PyTest(test_command):
    def run_tests(self):
        import pytest

        err_number = pytest.main(args=["tests"])
        sys.exit(err_number)


test_requirements = ["pytest"]


setup(name="hack_assemble",
      version="0.1",
      description="Assembles Hack assembly files into Hack machine language files.",
      long_description=long_description,
      classifiers=classifiers,
      keywords="hack assembler",
      python_requires=">=3.6",
      url="https://github.com/marcusmonteiro/coursera-nand2tetris/tree/master/projects/06/hack_assemble",
      author="Marcus Vinicius Monteiro de Souza",
      author_email="mvsouza007@gmail.com",
      license="MIT",
      packages=["hack_assemble"],
      cmdclass={"test": PyTest},
      tests_require=test_requirements,
      entry_points={
          "console_scripts": ["hack-assemble=hack_assemble.__main__:main"]},
      zip_safe=False)
