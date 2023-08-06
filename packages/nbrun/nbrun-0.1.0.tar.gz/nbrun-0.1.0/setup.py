import os
import setuptools


__version__ = '0.1.0'


def readfile(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), 'r') as f:
        return f.read()


setuptools.setup(
    name='nbrun',
    description="Verify that notebooks are runnable.",
    install_requires=[
        'click>=6.7',
        'nbconvert>=5.2.0,<6.0.0',
        'jupyter_client>=5.1.0,<6.0.0',
        'ipykernel>=4.6.0,<5.0.0',
        'tornado==4.5.3',
    ],
    extras_require={
        'dev': [
            'flake8',
            'pytest',
            'jupyter',
            'bumpversion',
        ],
    },
    keywords=["jupyter notebook test run runnable"],
    py_modules=['nbrun'],
    long_description=readfile('README.rst'),
    url="https://github.com/elgehelge/nbrun",
    entry_points='''
        [console_scripts]
        nbrun=nbrun:cli
    ''',
    version=__version__,
    maintainer="Helge Munk Jacobsen",
    maintainer_email="helgemunkjacobsen@gmail.com",
)
