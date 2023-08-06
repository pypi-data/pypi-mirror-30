from setuptools import setup
import sys

name = 'hakku'
version = '0.1.1'
description = 'Tool for article clustering based on word counts in titles and keywords.'
long_description = """
Hakku - tool for article clustering based on word counts in titles
and keywords. 

Clustering can be run from inside a script by run_files function or
from command line with python -m hakku articles1.txt articles2.txt
"""
author = 'Ilkka Pölönen, Tuomo Sipola, Paavo Nieminen, Jarno Kiesiläinen'
packages = ['hakku']
install_requires = ["numpy", "scipy", "nltk", "PyQt5", "ete3"]
zip_safe = False
package_data = {"hakku":["viridis.npy"]}
license="MIT"
python_requires = ">=3, <4"

setup(name=name,
        version=version,
        description=description,
        long_description=long_description,
        author=author,
        packages=packages,
        install_requires=install_requires,
        zip_safe=zip_safe,
        package_data=package_data,
        license=license,
        python_requires=python_requires
        )

