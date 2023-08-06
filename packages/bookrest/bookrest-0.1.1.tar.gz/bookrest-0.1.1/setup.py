from setuptools import find_packages, setup

version = "0.1.1"

setup(
    name='bookrest',
    version=version,
    url='https://www.agiliq.com/',
    author_email='hello@agiliq.com',
    long_description=open("README.md").read(),
    license='BSD',
    description='Web APIs for Django, made easy.',
    packages=find_packages(exclude=['example']),
)
