from setuptools import setup, find_packages
from letsplay import __version__

setup(name='letsplay',
      version=__version__,
      description='Extensible music player library for Python',
      url='http://github.com/marcinn/letsplay',
      author='Marcin Nowak',
      author_email='marcin.j.nowak@gmail.com',
      license='GPL3',
      packages=find_packages('.'),
      scripts=['bin/letsplay'],
      include_package_data=True,
      install_requires=[
          'pytaglib', 'observable', 'mplayer.py', 'pygobject',
          'dbus-python'],
      zip_safe=True)
