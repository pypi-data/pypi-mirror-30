from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
install_requires = [
    'numpy',
]
scripts = [
    'blib.py',
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
    version='0.1',
    description='For convenient coding.',
    long_description=long_description,
    # Choose your license
    license='NONE',
    packages=None,
    install_requires=install_requires,
    scripts=scripts,
)
