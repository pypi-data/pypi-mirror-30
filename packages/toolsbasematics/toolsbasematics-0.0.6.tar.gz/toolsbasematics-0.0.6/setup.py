# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='toolsbasematics',
    version='0.0.6',
    description='Tools for basematics',

    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://gene.pku.edu.cn',
    author='Xiannian Zhang',
    author_email='friedpine@gmail.com',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='sample setuptools development',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['peppercorn'],  # Optional

    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    package_data={  # Optional
        'sample': ['package_data.dat'],
    },

    data_files=[('my_data', ['data/data_file'])],  # Optional

    entry_points={  # Optional
        'console_scripts': [
            'toolssss=basematicstools:main',
        ],
    }
)
