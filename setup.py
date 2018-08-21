try:
    # Try using ez_setup to install setuptools if not already installed.
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    # Ignore import error and assume Python 3 which already has setuptools.
    pass

from setuptools import setup, find_packages

classifiers = ['Development Status :: Alpha',
               'Operating System :: POSIX :: Linux',
               'License :: OSI Approved :: MIT License',
               'Programming Language :: Python :: 2.7',
               'Topic :: System :: Hardware']

setup(name              = 'STAR',
      version           = '1.0.1',
      author            = 'Max Ferguson',
      author_email      = 'maxferg@stanford.edu',
      description       = 'Remote control for autonomous car',
      license           = 'MIT',
      classifiers       = classifiers,
      url               = 'https://github.com/maxkferg/mobile-robot-controller',
      #dependency_links  = ['https://github.com/adafruit/Adafruit_Python_GPIO/tarball/master#egg=Adafruit-GPIO-0.6.5'],
      #install_requires  = ['Adafruit-GPIO>=0.6.5'],
      packages          = find_packages())
