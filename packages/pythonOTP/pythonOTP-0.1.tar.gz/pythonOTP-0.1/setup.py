import os
from setuptools import setup, find_packages

def readme():
    with open("README.md", 'r', encoding='utf-8') as f:
        descript = f.read()
    return descript

tests_require = [
        'pytest',
        'pytest-cov',
        ]

setup(
        name='pythonOTP',
        version='0.1',

        description='OTP url for google-authenticator',
        long_description=readme(),

        license='MIT',

        author='deadlylaid',
        author_email='deadlylaid@gamil.com',

        tests_require=tests_require,

        packages=find_packages(),
        url='https://github.com/dealylaid/pythonOTP',
    )
