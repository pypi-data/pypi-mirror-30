#!python

from setuptools import setup

setup(name='protcomp', version='2.0',
      description='Python package to reconstruct protein complexes from protein pairwise interactions.',
      author='Ramon Massoni, Winona Oliveros',
      author_email='winn95@gmail.com',
      url='https://github.com/massonix/Python-project',
      py_modules=['multicomplex', 'multifunctions'], 
      entry_points={'console_scripts': ['multicomplex = multicomplex:main']},
      install_requires=['biopython'])

# it looks for the the modules in the "root" package, if there are not there, specify a package_dir option
# package_dir = {'': 'lib'}

# To create a source distribution for this module, run this on the terminal
# python setup.py sdist
# this will create an archive file (tarball/ZIP) containing the setup script and the specified modules.

# if and end user whises to install your module, has to download the tar file, unpack it, and from the directory created run:
# python setup.py install
