from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='ysmtool',
      version=version,
      description="simon's tool",
      long_description="""a simon's tool""",
      classifiers=[],
      keywords='simon,tool',
      author='simon',
      author_email='simon@yesiming.com',
      url='http://www.yesiming.com',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      )
