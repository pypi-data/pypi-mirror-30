from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    lic = f.read()

setup(
    name='catecs',
    version='0.1',
    description='A categorical entity component system',
    long_description=readme,
    author='Rik Hendriks',
    author_email='rikhendriks@rocketmail.com',
    url='https://github.com/RikHendriks/catecs',
    license=lic,
    packages=find_packages(exclude='tests')
)