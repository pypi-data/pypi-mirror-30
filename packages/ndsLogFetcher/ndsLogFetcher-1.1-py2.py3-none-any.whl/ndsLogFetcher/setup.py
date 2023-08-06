from setuptools import setup

setup(name='ndsLogFetcher',
      version='1.1',
      description='Log Fetcher',
      url='http://github.com/ckoksal/ndsLogFetcher',
      author='Cagri Koksal',
      author_email='koksal.cagri@gmail.com',
      license='none',
      packages=['ndsLogFetcher'],
      install_requires=['paramiko'],
      python_requires='>=3',
      zip_safe=False)