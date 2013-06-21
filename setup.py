from setuptools import setup
from setuptools import find_packages

setup(
    name="PythonPath",
    version="0.1",
    packages=find_packages(),
    author="Marcin Kowiel",
    author_email="marcin.kowiel@stxnext.pl",
    description="Python Path Project",
    package_dir={'': 'lib'},
    install_requires=['lxml'],
    entry_points={
        'console_scripts': [
            'noukaut = pythonpath.lib.nokaut.nokaut',
            'bar = othermodule:somefunc',
        ],
    }
)
