from setuptools import setup

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


requirements_kwargs = {
    'install_requires': [
        'socketIO-client-2',
    ]
}

setup(
    name='agario-bot',
    version='0.5',
    packages=['agario_bot'],
    description='Just small python bot client for socket-based agario',
    long_description=long_description,
    url='https://gitlab.com/unidev/agario-python-bot',
    python_requires='>=3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    **requirements_kwargs
)
