from __future__ import print_function
from setuptools import setup, find_packages
from subprocess import Popen, PIPE

def get_version():
  proc = Popen(["git", "describe"], stdout=PIPE)
  proc.wait()
  out, err = proc.communicate()
  
  if proc.returncode != 0:
    print("git describe returned %d" % proc.returncode)
    exit(proc.returncode)

  ver = out.decode("UTF-8")

  parts = ver.split("-")
  if len(parts) > 2:
    parts = parts[:2]

  return  '.'.join(parts)

version = get_version()

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

