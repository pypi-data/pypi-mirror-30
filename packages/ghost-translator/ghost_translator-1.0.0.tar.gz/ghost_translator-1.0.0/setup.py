
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ghost_translator',
    version='1.0.0',

    description='Finds translatable fields in your ghost theme and updates locale files.',
    long_description=long_description,

    url='https://github.com/arthurnoerve/ghost-translator',

    author='arthurnoerve',
    author_email='arthur@avgar.de',


    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='ghost translate handlebars',

    packages=find_packages(),

    install_requires=['peppercorn'],
    extras_require={ },

    entry_points={
        'console_scripts': [
            'ghost_translator=ghost_translator:main',
        ],
    }

)
