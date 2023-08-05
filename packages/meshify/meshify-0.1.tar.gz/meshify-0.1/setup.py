"""Install the script."""

from setuptools import setup

setup(
    name="meshify",
    version='0.1',
    description='Package to interact with the Meshify API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    py_modules=['meshify'],
    license="Apache 2.0",
    install_requires=[
        'Click',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        meshify=meshify:cli
        ''',
)
