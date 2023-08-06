from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='workon2',
      version=version,
      description="Project-management for your shell.",
      long_description="""\
This tool is build for people who work on multilpe projects and wish to speed up their development workflow.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='bash, shell, cli, pm, project management, navigation',
      author='Andre Lambert',
      author_email='afj.lambert@gmail.com',
      url='https://github.com/afjlambert/workon',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      scripts=['workon.sh'],
      install_requires=['click==6.7', 'PyYAML==3.12'],
      # entry_points="""
      # # -*- Entry points: -*-
      # """,
      entry_points = {
        'console_scripts': ['workon=workon.sh'],
      })
