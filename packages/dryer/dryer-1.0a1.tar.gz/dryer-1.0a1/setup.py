#!/usr/bin/env python

from setuptools import setup, find_packages
import versioneer

setup(
    name='dryer',
    version=versioneer.get_version(),
    description='coerce and serialize data structures',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords=['serialization'],
    url='http://py.errorist.io/dryer',
    license='MIT',
    cmdclass=versioneer.get_cmdclass()
)
