from setuptools import setup
setup(
  name = 'pyformulas',
  packages = ['pyformulas'],
  install_requires=[
          'opencv-python',
		  'numpy',
		  'urllib3'
      ],
  version = '0.2.2',
  description = 'A library of ready-to-go Python formulas',
  author = 'pyformulas',
  author_email = 'pyformulas@gmail.com',
  url = 'https://github.com/pyformulas/pyformulas',
  download_url = 'https://github.com/pyformulas/pyformulas/archive/0.2.2.tar.gz',
  keywords = ['python', 'formulas', 'recipes', 'cookbook', 'lazy', 'easy', 'quick', 'shortcut'],
  classifiers = [],
)