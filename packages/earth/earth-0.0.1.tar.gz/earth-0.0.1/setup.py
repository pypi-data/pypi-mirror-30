from setuptools import setup, find_packages
import os

# import __version__
exec(open('earth/_version.py').read())

install_requires = [
    'numpy'
    ]

setup(
    name='earth',
    version=__version__,
    author='Nathan Longbotham',
    author_email='nathan@descarteslabs.com',
    packages=find_packages(),
    description='All of it',
    # long_description=open('README.rst').read(),
    install_requires=install_requires
    # tests_require = tests_require,
    # scripts=['bin/run_spectral_conversions.py','bin/find_files.py']
)
