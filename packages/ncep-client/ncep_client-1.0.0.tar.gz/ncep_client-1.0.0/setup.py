# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='ncep_client',  # Required
    version='1.0.0',  # Required
    description='Communicates with NCEP product inventory servers and gets avaliable data.',  # Required
    url='https://github.com/AaronV77/NCEP_Data_Grabber',  # Optional
    author='Aaron Valoroso',  # Optional

    # This should be a valid email address corresponding to the author listed
    # above.
    author_email='valoroso99@gmail.com',  # Optional

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords=['ncep', 'product inventory'],  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages = find_packages(exclude=['build', 'docs', 'templates']),
)