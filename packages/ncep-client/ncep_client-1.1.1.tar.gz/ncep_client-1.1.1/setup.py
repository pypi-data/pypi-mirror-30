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
    name='ncep_client',
    version='v1.1.1',
    description='Communicates with NCEP product inventory servers and gets avaliable data.',
    long_description="Nothing",
    url='https://github.com/AaronV77/NCEP_Data_Grabber',
    author='Aaron Valoroso',
    author_email='valoroso99@gmail.com',
    license='BSD License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],    
    keywords=['ncep', 'product inventory'],
    packages = find_packages(exclude=['build', 'docs', 'templates']),
)
