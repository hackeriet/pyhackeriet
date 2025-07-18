from setuptools import setup, find_packages
import os

setup(
    name = "pyhackeriet",
    version = "0.1.2",
    author = "krav",
    description = ("Advanced Hackerspace Building Framework"),
    license = "WTFPL",
    packages=find_packages(),
    scripts=["bin/"+a for a in os.listdir("bin")],
    include_package_data=True,
    install_requires=[
      'flask',
      'paho-mqtt',
      'psycopg2',
      'pychromecast',
      'pynacl',
      'sqlalchemy',
      'stripe',
      'matrix_client',
    ],
    entry_points = {
       'console_scripts': [
                           'httpbridge=hackeriet.web.httpbridge:main',
                           'chromecast-snoop=hackeriet.chromecast:snoop',
                           'brusweb=hackeriet.web.brusweb:main',
                           'cardreaderd=hackeriet.cardreaderd:main',
                           'doorcontrold=hackeriet.doorcontrold:main'
                          ]
    }
)

