"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
long_description = ''
# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    # $ pip install uk_postcode_validator
    name='uk_postcode_validator',  # Required.
    version='1.0.0',  # Required
    description='A Python wrapper for Postcodes.io to validate and format UK postcodes.',  # Required
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='uk postcode validator python3 wrapper Postcodes.io',
    author='Jayakrishnan Damodaran',
    author_email='jayakrishnandamodaran@gmail.com',
    license='MIT',
    classifiers=[  # Optional
        'Development Status :: 5 - Production/Stable',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        # Pick your license as you wish
        'License :: MIT License',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    project_urls={
        'Source': 'https://github.com/jayakrishnandingit/uk_postcode_validator',
    },
    packages=find_packages(exclude=['contrib', 'docs']),
    install_requires=['requests>=2.18.4'],
    python_requires='>=2.7'
)
