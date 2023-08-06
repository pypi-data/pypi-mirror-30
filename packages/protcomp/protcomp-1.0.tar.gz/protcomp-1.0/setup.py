from distutils.core import setup


setup(name='protcomp',
	  description='Python package to reconstruct protein complexes from protein pairwise interactions.',
	  version = "1.0",
      author='Ramon Massoni and Winona Oliveros',
      author_email='winn95@gmail.com',
      py_modules=['multifunctions'],
      scripts=['multicomplex.py'])
