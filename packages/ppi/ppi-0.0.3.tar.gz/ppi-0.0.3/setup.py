from setuptools import setup, find_packages

setup(
    name='ppi',
    version='0.0.3',
    description='A command line tool help you to publish your python project on github and pypi',
    author='jeremaihloo',
    author_email='jeremaihloo1024@gmail.com',
    url='https://github.com/jeremaihloo/ppi',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    entry_points={
        'console_scripts': [
            'ppi=ppi:main',
        ],
    },
    install_requires=[
        'jsonpickle',
        'click'
    ],
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/jeremaihloo/ppi/issues',
        # 'Funding': 'https://donate.pypi.org',
        # 'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://github.com/jeremaihloo/ppi',
    },
)
