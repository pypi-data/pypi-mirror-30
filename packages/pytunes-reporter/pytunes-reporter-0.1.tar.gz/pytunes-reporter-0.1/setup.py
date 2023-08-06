from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pytunes-reporter',
    version='0.1',
    description='Library to interact with iTunes Reporter API',
    long_description=long_description,
    url='https://github.com/gifbitjapan/pytunes-reporter',
    author='Chason Chaffin',
    author_email='chason.c@routeone-power.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Office/Business :: Financial',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='itunes reporter financial sales',
    py_modules=["reporter"],
    install_requires=['requests'],
    extras_require={
        'test': ['pytest', 'faker', 'responses', 'pytest-responses'],
    },
    python_requires='>=3.6',
)
