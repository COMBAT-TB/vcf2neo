from setuptools import find_packages, setup
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='vcf2neo',
    version='0.0.8',
    url='https://github.com/COMBAT-TB/vcf2neo',
    bugtrack_url='https://github.com/COMBAT-TB/vcf2neo/issues',
    description='Parses SnpEff annotated VCF files and builds a graph '
                'database.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='neo4j,and vcf',
    license="GPLv3",
    py_modules=['vcf2neo'],
    packages=find_packages(),
    include_package_data=True,
    python_requires='~=3.6',
    install_requires=[
        'click',
        'bioservices',
        'py2neo==3.1.2',
        'tqdm',
        'PyVCF',
        'combattbmodel'
    ],
    dependency_links=[
        'https://test.pypi.org/simple/',
    ],
    entry_points={
        'console_scripts': ['vcf2neo=vcf2neo.cli:cli']
    },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Lavnguage :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
