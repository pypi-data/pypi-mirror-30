#!/usr/bin/env python

from setuptools import setup, find_packages
import os

MAJOR = 0
MINOR = 1
MICRO = 1
VERSION = '{}.{}.{}'.format(MAJOR, MINOR, MICRO)

ISRELEASED = False

setup_dir = os.path.abspath(os.path.dirname(__file__))
readme_file = os.path.join(setup_dir, 'README.md')

try:
    from m2r import parse_from_file
    README = parse_from_file(readme_file)
except ImportError:
    with open(readme_file) as f:
        README = f.read()


def write_version_py(filename=os.path.join(setup_dir, 'text_vectors/version.py')):
    version = VERSION
    if not ISRELEASED:
        version += '.dev'

    a = open(filename, 'w')
    file_content = "\n".join(["",
                              "# THIS FILE IS GENERATED FROM SETUP.PY",
                              "version = '%(version)s'",
                              "isrelease = '%(isrelease)s'"])

    a.write(file_content % {'version': VERSION,
                            'isrelease': str(ISRELEASED)})
    a.close()

write_version_py()

NAME = "text_vectors"
DESCRIPTION = ("Create text vectors in a robust way using GloVe or pre-built vectors only")
KEYWORDS = "text vectors"
AUTHOR = "Chapman Siu"
AUTHOR_EMAIL = "chapm0n.siu@gmail.com"
URL = 'https://github.com/chappers/text-vectors'
INSTALL_REQUIRES = ['m2r', 'scikit-learn', 'numpy', 'keras', 'nose', 'future'] # not in setup on purpose.

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    packages =find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    zip_safe=False # force install as source
)