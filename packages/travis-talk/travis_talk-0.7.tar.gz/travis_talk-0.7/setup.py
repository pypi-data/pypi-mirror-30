from setuptools import setup

setup(name='travis_talk',
      version=0.7,
      description='a testament to the arrogance and folly of man',
      author='rusty shackleford',
      license='none',
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      install_requires=[],
      packages=['travis_talk'],
      zip_safe=False,
      scripts=['travis_talk/bin/dumb-md5-hash'],
      entry_points= {
          'console_scripts': ['dumb-md5-hash=travis_talk.command_line:main']
      }
      )