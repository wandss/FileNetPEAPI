try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'FileNet Process Engine Python API',
    'author': 'Wanderley Souza',
    'url': 'https://github.com/wandss/FileNetPEAPI',
    'download_url': 'https://github.com/wandss/FileNetPEAPI',
    'author_email': 'wandss@gmail.com',
    'version': '1.2.0',
    'install_requires': ['nose', 'requests'],
    'packages': ['fnetpepAPI'],
    'scripts': [],
    'name': 'fnetpepAPI'
}

setup(**config)
