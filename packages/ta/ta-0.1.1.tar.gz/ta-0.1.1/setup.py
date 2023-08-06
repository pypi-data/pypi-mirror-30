from distutils.core import setup
setup(
    name = 'ta',
    packages = ['ta'],
    version = '0.1.1',
    description='Technical Analysis Library in Python',
    author = 'Dario Lopez Padial (Bukosabino)',
    author_email = 'bukosabino@gmail.com',
    url = 'https://github.com/bukosabino/ta',
    maintainer='Dario Lopez Padial (Bukosabino)',
    maintainer_email='bukosabino@gmail.com',
    install_requires=[
        'python3',
        'numpy',
        'pandas'
    ],
    download_url = 'https://github.com/bukosabino/ta/tarball/0.1',
    keywords = ['technical analysis', 'python3', 'pandas', 'numpy', 'fundamental analysis'],
    license='The MIT License (MIT)',
    classifiers = [],
)
