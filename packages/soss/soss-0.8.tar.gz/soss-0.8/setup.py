import os
import sys
from codecs import open

from setuptools import setup, find_packages

packages = ['soss']
requires = [
    'xmltodict>=0.11.0',
]

# Check Python version.
CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 4)
if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("""
SOSS requires Python {}.{}, but you're trying to
install it on Python {}.{}.
""".format(*(REQUIRED_PYTHON + CURRENT_PYTHON)))
    sys.exit(1)

EXCLUDE = ['README.md', '*.doc.py']

here = os.path.dirname(os.path.abspath(__file__))
about = {}
with open(os.path.join(here, 'soss', '__release__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)
setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=find_packages(exclude=EXCLUDE),
    include_package_data=True,
    # package_data={'': ['README', 'NOTICE'], 'soss': ['*.txt']},
    # package_dir={'soss': 'soss'},
    python_requires='>={}.{}'.format(*REQUIRED_PYTHON),
    install_requires=requires,
    license=about['__license__'],
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: Chinese (Simplified)',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
