from setuptools import setup
from os import path
import sys

here = path.abspath(path.dirname(__file__))
sys.path.insert(0, path.join(here, "protobuf_tools"))

import __version__ as version


def readme():
    with open('README.rst') as f:
        return f.read()


download_url = 'https://github.com/ajbansal/protobuf-tools/archive/{}.tar.gz'.format(version.package_version)

setup(name='protobuf_tools',
      version=version.package_version,
      long_description=readme(),
      test_suite='nose.collector',
      tests_require=['nose'],
      description='A library for adding some usability tools for working with protobuf',
      url='https://github.com/ajbansal/protobuf-tools',
      author='Abhijit Bansal',
      author_email='pip@abhijitbansal.com',
      license='MIT',
      packages=['protobuf_tools'],
      zip_safe=False,
      entry_points={'console_scripts': ["protobuftools=protobuf_tools.proto_utils:main"]},
      install_requires=["protobuf==3.5.2",
                        "pathlib2==2.3.0"],
      include_package_data=True,
      classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.6',
            'Topic :: Software Development :: Code Generators',
      ],
      )
