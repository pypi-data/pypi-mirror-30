from distutils.core import setup

setup(
  name = 'pyMidWiki',
  packages = ['pymediawiki'], 
  version = '0.1',
  description = 'Python Wrapper for MediaWiki API',
  author = 'Simon De Greve',
  author_email = 'degrevesim@gmail.com',
  url = 'https://github.com/Yoiro/pymediawiki', 
  keywords = ['mediawiki', 'api', 'wiki'], 
  classifiers = [
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
  install_requires=[
    'requests>=2.18.4',
  ],
  python_requires='>=3',
)
