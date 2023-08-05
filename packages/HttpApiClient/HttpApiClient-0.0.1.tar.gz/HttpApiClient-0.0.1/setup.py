from setuptools import setup, find_packages

setup(
    name='HttpApiClient',
    version='0.0.1',
    packages=find_packages(),
    author='smp.io',
    author_email='dev@smp.io',
    url='https://github.com/smpio/HttpApiClient',

    install_requires=[
        'six==1.11.0',
        'requests==2.18.4',
        'jsonschema==2.6.0',
    ],
)
