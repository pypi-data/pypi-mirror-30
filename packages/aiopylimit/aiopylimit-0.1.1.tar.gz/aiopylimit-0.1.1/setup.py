from distutils.core import setup
setup(
  name = 'aiopylimit',
  packages = ['aiopylimit'],
  description = 'A distributed rate limiting library for python using leaky bucket algorithm and Redis(asyncio version)',
  author='David Markey',
  version='0.1.1',
  author_email='david@dmarkey.com',
  url='https://github.com/dmarkey/aiopylimit',
  keywords=['rate limiting', 'throttle', 'redis', 'asyncio'],
  classifiers=[],
)
