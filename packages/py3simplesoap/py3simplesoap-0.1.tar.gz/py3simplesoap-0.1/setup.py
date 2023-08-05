from distutils.core import setup

setup(
  name = 'py3simplesoap',
  packages = ['py3simplesoap'], # this must be the same as the name above
  version = '0.1',
  description = 'pysimplesoap for python3',
  author = 'Mastercore',
  author_email = 'far@mastercore.net',
  # use the URL to the github repo
  url = 'https://github.com/odoo-mastercore/pysimplesoap',
  download_url = 'https://github.com/odoo-mastercore/pysimplesoap/tarball/0.1',
  keywords = ['py3simplesoap', 'py3'],
  classifiers = [
      # How mature is this project? Common values are
      #   3 - Alpha
      #   4 - Beta
      #   5 - Production/Stable
      'Development Status :: 4 - Beta',

      # Indicate who your project is intended for
      'Intended Audience :: Developers',
      'Topic :: Software Development :: Build Tools',

      # Specify the Python versions you support here. In particular, ensure
      # that you indicate whether you support Python 2, Python 3 or both.
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.2',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
  ],
)
