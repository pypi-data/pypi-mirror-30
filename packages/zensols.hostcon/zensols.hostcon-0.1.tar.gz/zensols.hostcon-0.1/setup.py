from setuptools import setup, find_packages

setup(
    name = "zensols.hostcon",
    packages = ['zensols.hostcon'],
    version = '0.1',
    description = 'This is a simple program to load servers from a file, list them, then allow you to login, SSH mount, etc.',
    author = 'Paul Landes',
    author_email = 'landes@mailc.net',
    url = 'https://github.com/plandes/hostcon',
    download_url = 'https://github.com/plandes/hostcon/releases/download/v0.0.1/zensols.hostcon-0.1-py3-none-any.whl',
    keywords = ['tooling'],
    entry_points={
        'console_scripts': [
            'hostcon=zensols.hostcon.cli:main'
        ]
    },
    classifiers = [],
)
