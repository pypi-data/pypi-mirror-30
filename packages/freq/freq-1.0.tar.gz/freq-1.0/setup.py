from distutils.core import setup

setup(
  name = 'freq',
  packages = ['freq'],
  package_dir = {'freq': 'freq'},
  package_data = {'freq': ['__init__.py']},
  version = '1.0',
  description = 'Frequency Calculator for Python',
  author = 'Daniel J. Dufour',
  author_email = 'daniel.j.dufour@gmail.com',
  url = 'https://github.com/DanielJDufour/freq',
  download_url = 'https://github.com/DanielJDufour/freq/tarball/download',
  keywords = ['counter', 'dict', 'frequency'],
  classifiers = [],
  install_requires=[]
)
