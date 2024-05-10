from setuptools import setup

setup(
    name='schema_tools',
    version='0.0.1',
    packages=['schema_tools'],
    install_requires=[
        'Jinja2==3.1.3',
        'cookiecutter==2.6.0',
        'pydantic-settings==2.2.1',
    ]
)