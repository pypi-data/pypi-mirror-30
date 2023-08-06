from setuptools import setup

__version__ = "0.1.1"

with open('README.rst') as f:
    long_description = f.read()

setup(
    name="spgateway-core",
    version=__version__,
    description='Spgateway core libary',
    keywords="spgateway",
    author="CJLTSOD <github.tsod@tsod.idv.tw>",
    author_email="github.tsod@tsod.idv.tw",
    url="https://github.com/cjltsod/django-spgateway",
    license="MIT",
    packages=["spgateway_core"],
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
    ],
    long_description=long_description,
)
