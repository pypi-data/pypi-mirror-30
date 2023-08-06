from setuptools import find_packages, setup
from os import path

with open("README.md") as readme_file:
    readme = readme_file.read()

about = {}
with open(path.join("ledge", "__about__.py")) as fp:
    exec(fp.read(), about)

requirements = [
    "numpy",
    "pandas",
    "xarray"
]

setup(
    name="ledge",
    version=about["__version__"],
    description="Hedging algorithms with lag",
    long_description=readme,
    author=about["__author__"],
    author_email=about["__email__"],
    url="https://github.com/reichlab/ledge",
    install_requires=requirements,
    keywords="",
    license="GPLv3",
    packages=find_packages(),
    classifiers=(
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only"
    ))
