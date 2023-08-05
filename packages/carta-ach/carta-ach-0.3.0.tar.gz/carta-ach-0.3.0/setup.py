from distutils.core import setup

setup(
    name='carta-ach',
    author='Travis Hathaway',
    author_email='travis.j.hathaway@gmail.com',
    version='0.3.0',
    packages=[
        'ach',
    ],
    url='https://github.com/carta/python-ach',
    license='MIT License',
    description='Library to create and parse ACH files (NACHA)',
    long_description=open('README.rst').read(),
)
