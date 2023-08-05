from setuptools import setup, find_packages

setup(
    name='bngl',
    version='0.1.0',
    author='Brandon Duderstadt',
    description='Bstadt\'s NeuroGraph Library',
    url='https://github.com/bstadt/bngl.git',
    install_requires=['numpy'],
    packages = find_packages()
)
