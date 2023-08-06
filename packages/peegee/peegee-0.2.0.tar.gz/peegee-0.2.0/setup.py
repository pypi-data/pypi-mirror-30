from distutils.core import setup
VERSION = '0.2.0'
setup(
    name = 'peegee',
    packages = ['peegee'],
    version = VERSION,
    description = 'A pythonic PostgreSQL client based on psycopg2 suit only for Python3',
    install_requires=['psycopg2',],
    author = 'scku',
    author_email = 'scku208@gmail.com',
    url = 'https://github.com/scku208/peegee',
    download_url = 'https://github.com/scku208/peegee/archive/{v}.tar.gz'.format(v=VERSION),
    keywords = ['postgresql', 'psycopg2', 'database'],
    classifiers = [],
)