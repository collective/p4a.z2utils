from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='p4a.z2utils',
      version=version,
      description="Miscellaneous utilities for Zope 2",
      long_description="""""",
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
