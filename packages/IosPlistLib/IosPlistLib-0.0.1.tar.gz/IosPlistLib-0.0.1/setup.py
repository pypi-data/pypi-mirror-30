from setuptools import setup, find_packages
import iosplistlib

with open('README.md') as f:
    long_desc = f.read()

setup(name='IosPlistLib',
      version='0.0.1',
      description='Display and edit settings within an ipa Root.plist file in an iOS ipa.',
      long_description=long_desc,
      url='https://github.com/mkurdian/IosPlistLib',
      author='Manuel Kurdian',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Topic :: Utilities',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          ],
      keywords="iOS plist ipa",
      packages=find_packages(),
      entry_points={
        'console_scripts': [
            'iosplistlib=iosplistlib.iosplistlib:main',
            ]
        }
      )