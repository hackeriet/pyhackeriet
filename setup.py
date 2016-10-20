from setuptools import setup, find_packages
import os

setup(
    name = "pyhackeriet",
    version = "0.0.1",
    author = "krav",
    description = ("Advanced Hackerspace Building Framework"),
    license = "WTFPL",
    packages=find_packages(),
    scripts=["bin/"+a for a in os.listdir("bin")],
    include_package_data=True,
    entry_points = {
       'console_scripts': ['httpbridge=hackeriet.web.httpbridge:main'] 
    }
#    tests_require=['piytest'],
#    test_suite = 'pytest'
)
