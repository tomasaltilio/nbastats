from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as f:
    content = f.readlines()
requirements = [x.strip() for x in content if 'git+' not in x]

setup(name='NBA_stats',
      version="1.0",
      description="Project Description",
      packages=find_packages(),
      install_requires=requirements,
      test_suite='tests',
      include_package_data=True, # include_package_data: to install data from MANIFEST.in
      zip_safe=False)
