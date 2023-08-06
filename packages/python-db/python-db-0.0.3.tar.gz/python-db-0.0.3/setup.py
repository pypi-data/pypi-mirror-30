from distutils.core import setup
setup(
    name = 'python-db',
    packages = ['pydb'],
    version = "0.0.3",
    description = 'Placeholder description',
    author = "Jason Trigg",
    author_email = "jasontrigg0@gmail.com",
    url = "https://github.com/jasontrigg0/python-db",
    download_url = 'https://github.com/jasontrigg0/python-db/tarball/0.0.3',
    scripts=['bin/db'],
    install_requires=['mysqldb',
                      'argparse',
                      'jtutils',
                      'python-csv'
    ],
    keywords = [],
    classifiers = [],
)
