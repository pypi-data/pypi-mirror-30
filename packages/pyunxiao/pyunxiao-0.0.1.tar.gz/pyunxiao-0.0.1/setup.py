from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="pyunxiao",
    version="0.0.1",
    author="ChenQiuQiang",
    author_email="chenqiuqiang@iyunxiao.com",
    description="A Python library for handwritten digit recognition.",
    long_description=open("README.rst").read(),
    license="MIT",
    #url="https://github.com/WEIHAITONG1/better-youtubedl",
    packages=['pyunxiao'],
    classifiers=[
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: Education',
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=True,
)
