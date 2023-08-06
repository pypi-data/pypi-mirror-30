from setuptools import setup, find_packages
import os.path
#from distutils.core import setup
setup(
  name = 'sparkworks',
  packages=['sparkworks'],
  version = '0.1.3',
  description = 'A client library for the sparkworks api',
  author = 'SparkWorks ITC',
  author_email = 'info@sparkwokrs.net',
  url = 'http://sparkworks.net', # use the URL to the github repo
  download_url = 'https://github.com/SparkWorksnet/client', # I'll explain this in a second
  keywords = ['client', 'sparkworks'], # arbitrary keywords
  include_package_data=True,
  classifiers = [],
)
