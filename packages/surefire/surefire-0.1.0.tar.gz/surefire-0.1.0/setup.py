from setuptools import setup, find_packages

VERSION = '0.1.0'

setup(
    name='surefire',
    version=VERSION,
    author='Jason Kriss',
    author_email='jasonkriss@gmail.com',
    url='https://github.com/jasonkriss/surefire',
    description='PyTorch models for structured data',
    license='MIT',
    packages=find_packages(),
    zip_safe=True,
    install_requires=[
        'torch'
    ]
)
