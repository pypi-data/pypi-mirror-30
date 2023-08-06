from __future__ import print_function
from setuptools import setup, find_packages
from subprocess import Popen, PIPE

version="1.2.8"

print("Building python-csiot version %s" % version)
setup(
		name="csiot",
		version=version,
		author="Kevin Morris",
		author_email="kevin.morris@codestruct.net",
		description="CSIoT Python SDK",
		url="https://codestruct.net",
		packages=find_packages()
)

