from distutils.core import setup

setup(
    # Application name:
    name="Scrap_Sensa",

    # Version number (initial):
    version="1.0.0",

    # Application author details:
    author="Pepe Mdrano",
    author_email="pepemedranogomez@icloud.com",

    # Packages
    packages=["app"],

    # Dependent packages (distributions)
    install_requires=[
        'requests',
        'bs4',
        'json'
    ],
)