from setuptools import setup, find_packages
import sys, os

version = '0.12'

setup(name='csnotifier',
      version=version,
      description="A product to send notifications to Pushwosh or Firebase",
      long_description=open("README.rst").read() + "\n" + open("HISTORY.txt").read(),
      classifiers=[],
      keywords='',
      author='CodeSyntax',
      author_email='info@codesyntax.com',
      url='https://codesyntax.com',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'requests'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
