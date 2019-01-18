from setuptools import find_packages, setup

setup(
    name='vcf2neo',
    version='0.0.7',
    description='Parses SnpEff annotated VCF files and builds a graph '
                'database.',
    keywords='neo4j,and vcf',
    py_modules=['vcf2neo'],
    packages=find_packages(),
    include_package_data=True,
    dependency_links=[
        'git+https://github.com/COMBAT-TB/combattbmodel.git#egg=combattbmodel-0.0.6'],
    install_requires=[
        'click',
        'bioservices',
        'py2neo==3.1.2',
        'tqdm',
        'PyVCF',
        'combattbmodel'
    ],
    entry_points={
        'console_scripts': ['vcf2neo=vcf2neo.cli:cli']
    },
)
