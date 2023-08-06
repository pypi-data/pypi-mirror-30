from setuptools import setup

setup(
    name='dnaconverter2',
    version='1.0.1',
    description='an algorithm to encode any file into a sequence of ACGT',
    license='MIT',
    packages=['dnaconverter2'],
    entry_points = {
        'console_scripts': ['dnaconverter2=dnaconverter2.dna:main'],
    },
    author='Anshul Khanna',
    author_email='anshul17khanna@gmail.com',
    keywords=['dnaconverter'],
    url=''
)
