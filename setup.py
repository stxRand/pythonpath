from setuptools import setup
from setuptools import find_packages

setup(
    name="PythonPath",
    version="0.1",
    packages=find_packages(),
    author="Marcin Kowiel",
    author_email="marcin.kowiel@stxnext.pl",
    description="Python Path Project",
    test_suite="tests",
    install_requires=['lxml', 'mock'],
    entry_points={
        'console_scripts': [
            'nokaut = pythonpath.nokaut:main'
        ],
    }
)
