from setuptools import setup

setup(
    name='schema_tools_alembic',
    version='0.0.1',
    packages=['schema_tools_alembic'],
    package_data={'': ['layout/**', 'templates/**', 'Dockerfile']},
    include_package_data=True,
    install_requires=[
        'schema_tools @ git+https://github.com/quark-tekliner/schema_tools/#egg=schema_tools&subdirectory=schema_tools',
        'black==24.4.0',
    ]
)