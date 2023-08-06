"""
A proxy for installing seleniumbase dependencies and plugins
"""

from setuptools import setup, find_packages  # noqa

setup(
    name='selenium-base',
    version='0.1.0',
    description='Web Automation & Testing Framework - http://seleniumbase.com',
    long_description='Web Automation and Testing Framework - seleniumbase.com',
    platforms='Mac * Windows * Linux * Docker',
    url='http://seleniumbase.com',
    author='Michael Mintz',
    author_email='mdmintz@gmail.com',
    maintainer='Michael Mintz',
    license='The MIT License',
    install_requires=[
        'seleniumbase',
        ],
    packages=[
        ],
    entry_points={
        'nose.plugins': [
            ],
        'pytest11': [
            ]
        }
    )

print("\n*** SeleniumBase Installation Complete! ***\n")
