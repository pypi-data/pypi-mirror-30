from distutils.core import setup

setup(
  name = 'pmemoize',
  version = '1.0',
  py_modules = ['pmemoize'],
  description = 'Memoizer with optional persistence to disk',
  long_description = (
'''
Yet another memoizer. I have been using this for a long time. It is simple but
useful. Features:

* Optional persistence to disk, using pickle to save the cache on exit.
* Configurable cache size. When it is reached a FIFO strategy is used to
  discard old entries.
* Stats tracking. Allows to see if memoization is useful for a certain function
  call.
'''
),
  author = 'Giorgos Tzampanakis',
  author_email = 'giorgos.tzampanakis@gmail.com',
  url = 'https://github.com/gtzampanakis/pmemoize',
  download_url = 'https://github.com/gtzampanakis/pmemoize/archive/1.0.tar.gz',
  keywords = ['memoize'],
  classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
  ],
)
