from setuptools import setup

setup(
    name='combat_tb_model',
    version='0.0.3',
    description='COMBAT-TB Graph Model,a Chado-derived graph model for genome annotation.',
    keywords='neo4j',
    packages=['combat_tb_model', 'combat_tb_model.model'],
    install_requires=[
        'py2neo'
    ]
)
