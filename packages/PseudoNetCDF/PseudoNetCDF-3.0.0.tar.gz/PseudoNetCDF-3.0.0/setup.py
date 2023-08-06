from __future__ import print_function
try:
    from setuptools import setup
except:
    from distutils.core import setup
import os
import sys
from warnings import warn
def find_packages():
    import os
    packages = []
    walker = os.walk('src')
    prefix = os.path.join(os.path.curdir,'src')
    for thisdir, itsdirs, itsfiles in walker:
        if '__init__.py' in itsfiles:
            packages.append(thisdir[len(prefix)-1:])
    
    return packages
            
def find_data():
    import os
    import re
    data_pattern = re.compile(r'.*(.|_)(yaml|nc|net|irr|phy|ptb|sum|voc|txt|xls|graffle)$')
    data = []
    prefix = os.path.join(os.path.curdir,'src', 'PseudoNetCDF')
    walker = os.walk('src')
    for thisdir, itsdirs, itsfiles in walker:
        if thisdir != os.path.join('src','PseudoNetCDF.egg-info'):
            data.extend([os.path.join(thisdir[len(prefix)-1:],f) for f in itsfiles if data_pattern.match(f) is not None])
    
    return data

packages = find_packages()
data = find_data()

setup(name = 'PseudoNetCDF',
      version = '3.0.0',
      author = 'Barron Henderson',
      author_email = 'barronh@gmail.com',
      maintainer = 'Barron Henderson',
      maintainer_email = 'barronh@gmail.com',
      description = 'Like NetCDF and NCO, but works with NetCDF and other scientific formats.',
      long_description = """NetCDF, NCO, and CDO are fantastic softwares that I use, emulate, and admire. The primary drawbacks are restrictions on which scientific data sources they will and won't work with, and what types of operations they will and won't do. PseudoNetCDF was originally just a NetCDF-like interface for many data formats, but has grown to include amny functionalities from NCO and CDO. This is a platform independent, easy to install software to make scientific data manipulation easy.""",
      packages = packages,
      package_dir = {'': 'src'},
      package_data = {'PseudoNetCDF': data},
      scripts = ['scripts/pncmadis2pnceval.py', 'scripts/pncaqsraw4pnceval.py', 'scripts/pncaqsrest4pnceval.py', 'scripts/pncasos4pnceval.py', 'scripts/pnc1d.py', 'scripts/pnc2d.py', 'scripts/pncboundaries.py', 'scripts/pncdiurnal.py', 'scripts/pncdump', 'scripts/pncdump.py', 'scripts/pnceval', 'scripts/pnceval.py', 'scripts/pncgen', 'scripts/pncgen.py', 'scripts/pncglobal2cmaq.py', 'scripts/pncload', 'scripts/pncmap.py', 'scripts/pncqq.py', 'scripts/pncscatter.py', 'scripts/pncts.py', 'scripts/pncvertprofile.py', 'scripts/pncview', 'scripts/pncview.py', 'scripts/pncwindrose.py'],
      install_requires = ['numpy>=1.2', 'netCDF4', 'scipy', 'matplotlib', 'pyyaml'],
      extras_require = {'textfiles': ['pandas'],
                        'projections': ['pyproj'],
                        'mapping': ['basemap'],},
      url = 'http://github.com/barronh/pseudonetcdf/',
      classifiers = ['Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3',
                     'Operating System :: MacOS',
                     'Operating System :: Microsoft :: Windows',
                     'Operating System :: POSIX',
                     'Topic :: Scientific/Engineering',
                     'Topic :: Scientific/Engineering :: Atmospheric Science',
                    ]
      )
