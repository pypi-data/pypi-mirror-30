from setuptools import setup

setup(
    name = 'asit',
    packages = ['asit'],
    version = '0.3',
    description = 'Advanced System Information Toolbox Python Library',
    author = 'Ali Gholami', 
    author_email = 'aligholami7596@gmail.com',
    url = 'https://github.com/aligholamee/asit',
    keywords = 'SYSTEM INFO CPU MEMORY OS PYTHON',
    platforms = ["any"],
    install_requires = [
        'codecov'
    ],
    python_requires = '>3.5',
    license = 'MIT'
)
