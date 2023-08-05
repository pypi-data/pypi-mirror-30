import os
from setuptools import setup, find_packages

tests_require = [
        'pytest',
        'pytest-cov',
        ]

setup(
        name='pythonOTP',
        version='0.2',

        description='OTP url for google-authenticator',

        license='MIT',

        author='deadlylaid',
        author_email='deadlylaid@gamil.com',

        tests_require=tests_require,

        packages=find_packages(),
        url='https://github.com/dealylaid/pythonOTP',
    )
