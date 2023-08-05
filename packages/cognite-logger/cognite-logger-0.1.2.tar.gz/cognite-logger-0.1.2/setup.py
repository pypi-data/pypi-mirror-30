from distutils.core import setup
import cognite_logger

setup(
    # Application name:
    name="cognite-logger",

    # Version number (initial):
    version=cognite_logger.__version__,

    # Application author details:
    author="Stian Lågstad",
    author_email="stian.lagstad@cognite.com",

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/cognitedata/python-logger",

    packages=['cognite_logger'],

    description="Simple logging wrapper.",

    # Dependent packages (distributions)
    install_requires=[
        "python-json-logger==0.1.8"
    ],
)
