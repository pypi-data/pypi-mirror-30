from setuptools import setup
setup(
  name = 'aiopylimit',
  packages = ['aiopylimit'],
  description = 'A distributed rate limiting library for python using leaky bucket algorithm and Redis(asyncio version)',
  author='David Markey',
  author_email='david@dmarkey.com',
  use_scm_version=True,
  setup_requires=['setuptools_scm'],
  url='https://github.com/dmarkey/aiopylimit',
  install_requires=[
      'aioredis<=1.1.0',
  ],
  keywords=['rate limiting', 'throttle', 'redis', 'asyncio'],
  classifiers=[],
)
