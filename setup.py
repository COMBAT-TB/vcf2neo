from setuptools import setup

setup(
    name='vcf2neo',
    version='0.0.1',
    description='Parses VCF file and builds a graph database.',
    keywords='neo4j,and vcf',
    py_modules=['vcf2neo'],
    install_requires=[
        'click',
        'bioservices',
        'py2neo'
    ],
    entry_points={
        'console_scripts': ['vcf2neo=vcf2neo.cli:cli']
    },
)
