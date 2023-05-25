from setuptools import setup, find_packages

setup(
    name='wecomsan',
    version='0.1',
    author='Barry ZZJ',
    description='wecom interface api',
    packages=find_packages(),
    install_requires=[
        # list any dependencies your package requires
        'requests'
    ],
)
