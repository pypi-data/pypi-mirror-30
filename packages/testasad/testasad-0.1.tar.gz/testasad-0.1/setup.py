
from setuptools import setup, find_packages

setup(
    name='testasad',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Datorama Python Package',
    long_description=open('README.txt').read(),
    install_requires=[],
    url='https://github.com/datorama/python-connector-package',
    author='Asaad Awesat',
    author_email='asaad.awesat@datorama.com'
)
