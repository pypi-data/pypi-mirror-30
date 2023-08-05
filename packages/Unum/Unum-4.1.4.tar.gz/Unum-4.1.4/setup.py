from setuptools import setup

__version_info__ = (4, 1, 4)
__version__ = '.'.join([str(v) for v in __version_info__])
setup(name = "Unum",
      version = __version__,
      description  = "Units in Python",
      author = "Chris MacLeod, Pierre Denis",
      author_email = "ChrisM6794@gmail.com",
      url = "http://bitbucket.org/kiv/unum/",
      tests_require=['nose>=0.11'],
      test_suite="nose.collector",
      license = "LGPL",
      packages = ('unum',
                  'unum.units',
                  'unum.units.custom',
                  'unum.units.others',
                  'unum.units.si',
                  'tests',
      )
)
