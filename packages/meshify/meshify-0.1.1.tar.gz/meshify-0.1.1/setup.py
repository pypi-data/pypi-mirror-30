"""Install the script."""

from setuptools import setup
try:
    import pypandoc
    description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    description = open('README.md', 'r').read()


setup(
    name="meshify",
    version='0.1.1',
    description='Package to interact with the Meshify API',
    long_description=description,
    long_description_content_type='text/x-rst',
    py_modules=['meshify'],
    license="Apache 2.0",
    author='Patrick McDonagh',
    author_email='patrickjmcd@gmail.com',
    install_requires=[
        'Click',
        'requests'
    ],
    keywords='meshify api cloud',
    project_urls={
        'Source': 'https://github.com/patrickjmcd/Meshify-Python-API/',
        'Tracker': 'https://github.com/patrickjmcd/Meshify-Python-API/issues',
    },
    entry_points='''
        [console_scripts]
        meshify=meshify:cli
        ''',
)
