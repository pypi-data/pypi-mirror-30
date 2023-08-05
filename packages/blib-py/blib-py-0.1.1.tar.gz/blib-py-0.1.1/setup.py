from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
install_requires = [
    'numpy',
    'cycler',
    'matplotlib'
]
scripts = [
    '__init__.py',
    'colors.py'
]
console_scripts = [
    'gui=gui.__main__:main'
]
gui_scripts = []

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()
setup(
    name='blib-py',
    version='0.1.1',
    description='For convenient coding and colormaps.',
    url='https://github.com/boonleng/blib-py',
    author='Boonleng Cheong',
    author_email='boonleng@ou.edu',
    license='MIT',
    packages=['blib'],
    install_requires=install_requires,
    zip_safe=False
)
