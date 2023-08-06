from setuptools import setup  # type: ignore

setup(
    name='edpanalyst',
    packages=['edpanalyst'],
    version='0.1.13',
    description='The python API to the Empirical Data Platform.',
    license='Apache License 2.0',
    install_requires=[
        'beautifulsoup4', 'configparser', 'future', 'natsort', 'pandas',
        'requests', 'typing', 'enum34'
    ]
)  # yapf: disable
