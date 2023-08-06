from setuptools import setup, find_packages

setup(
    # Application name:
    name="tbox",

    # Version number (initial):
    version="1.0",

    # Application author details:
    author="Mauricio Quatrin",
    author_email="mqg@technobox.com.br",

    # Packages
    packages=find_packages(),

    # Include additional files into the package
    include_package_data=True,

    url="http://www.technobox.com.br",

    # entry_points = {
    #     'console_scripts': ['tpkg=tbox.tpkg.tpkg:main'],
    # },

    #
    #license="",
    description="TechnoBox Namespace",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
    ],
)