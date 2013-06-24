from setuptools import setup
from setuptools import find_packages

setup(
    name="PythonPath",
    version="0.2",
    packages=find_packages(),
    author="Marcin Kowiel",
    author_email="marcin.kowiel@stxnext.pl",
    description="Python Path Project",
    test_suite="tests",
    install_requires=['lxml', 'mechanize', 'BeautifulSoup', 'mock'],
    entry_points={
        'console_scripts': [
            'nokaut = pythonpath.nokaut:main'
        ],
    }
)
