#!/usr/bin/env python
install_requires= ['python-dateutil','pytz','numpy','xarray',
                   'sciencedates','gridaurora']
tests_require = ['pytest','nose','coveralls']
# %%
from setuptools import find_packages
from numpy.distutils.core import setup,Extension

setup(name='msise00',
      packages=find_packages(),
      description='Python API for Fortran MSISE-00 neutral atmosphere model.',
      author='Michael Hirsch, Ph.D.',
      version='1.1.1a',
      url='https://github.com/scivision/msise00',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3.6',
      ],
      ext_modules=[Extension(name='gtd7',
                sources=['fortran/nrlmsise00_sub.for'],
                f2py_options=['--quiet'])],
      install_requires=install_requires,
      tests_require=tests_require,
      python_requires='>=3.6',
      extras_require={'plot':['matplotlib','seaborn'],
                      'io':['astropy','pymap3d'],
                      'tests':tests_require},
      script=['RunMSIS.py'],
      include_package_data=True,
	  )

