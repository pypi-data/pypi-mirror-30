'''
A python package for EDA
'''
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()


# Main setup function
setup(
    name = "pykhoj",
    version = "1.0.dev2",
    description = "Python package for exploratory data analysis",
    long_description=long_description,
    url = "https://github.com/sagarkar10/pykhoj",
    author = "Sagar Kar",
    author_email = "sagarkar10@gmail.com",

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(exclude=['tests']),  # Required
    # Include other packeges that pykhoj depends on
    install_requires=['numpy','pandas','matplotlib','seaborn'],
    # Include optional data files needed for package
    package_data={
            },
)
