from setuptools import find_packages, setup


with open('README.md') as file:
    long_description = file.read()

setup(
    name='puregym',
    version='0.1.0',
    description='Module for interacting with PureGym.',
    long_description=long_description,
    url='https://github.com/thomasleese/pypuregym',
    author='Thomas Leese',
    author_email='thomas@leese.io',
    packages=find_packages(),
    install_requires=[
        'requests',
        'lxml',
        'cssselect',
        'esprima',
        'cached-property',
        'selenium',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)
