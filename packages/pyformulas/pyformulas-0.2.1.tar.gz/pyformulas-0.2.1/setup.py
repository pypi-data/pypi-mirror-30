from distutils.core import setup
setup(
  name = 'pyformulas',
  packages = ['pyformulas'],
  install_requires=[
          'opencv>=3.3.1',
		  'numpy',
		  'urllib3'
      ],
  version = '0.2.1',
  description = 'A library of ready-to-go Python formulas',
  author = 'pyformulas',
  author_email = 'pyformulas@gmail.com',
  url = 'https://github.com/pyformulas/pyformulas',
  download_url = 'https://github.com/pyformulas/pyformulas/archive/0.2.1.tar.gz',
  keywords = ['python', 'formulas', 'recipes', 'cookbook', 'lazy', 'easy', 'quick', 'shortcut'],
  classifiers = [],
)