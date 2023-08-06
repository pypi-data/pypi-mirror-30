# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#   long_description = f.read()

setup(
  name = 'torchdv',
  packages = ['torchdv'], # this must be the same as the name above
  version = '0.3',
  description = 'Deep Visualization in pytorch',
  author = 'Maitreya Patel',
  author_email = 'patel.maitreya57@gmail.com',
  # url = 'https://github.com/Maitreyapatel/Deep-Visualization', # use the URL to the github repo
  # download_url = 'https://github.com/Maitreyapatel/Deep-Visualization/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['Pytorch', 'deep visualization', 'torchdv'], # arbitrary keywords
  classifiers = [],
)
