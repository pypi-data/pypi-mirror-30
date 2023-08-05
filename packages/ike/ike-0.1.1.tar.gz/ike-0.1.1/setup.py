#!/usr/bin/env python3

from setuptools import setup
from ike import __version__

def readme():
    with open('docs/readme.rst') as f:
        return f.read()


setup(name='ike',
      version='.'.join('{}'.format(x) for x in __version__),
      description='Minimalistic Internet Key Exchange protocol v2 (RFC 5996) library',
      long_description=readme(),
      author='Kimmo Parviainen-Jalanko',
      author_email='k@77.fi',
      url='http://github.com/kimvais/ike/',
      download_url='https://github.com/kimvais/ike/releases',
      packages=['ike', 'ike.util'],
      install_requires=[
          'rsa',
          'cryptography'
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Unix',
          'Programming Language :: Python :: 3.4',
          'Topic :: Communications',
          'Topic :: Internet',
          'Topic :: Security',
          'Topic :: Security :: Cryptography',
      ]
)
