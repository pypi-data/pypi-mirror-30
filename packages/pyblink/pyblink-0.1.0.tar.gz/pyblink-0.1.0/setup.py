from setuptools import setup, find_packages
from os import path

from pyblink.__init__ import __version__

setup(
    name='pyblink',
    packages=find_packages(exclude=['tests']),
    version=__version__,
    description='Compute in a blink with Google Cloud Platform',
    author = 'Thomas Ounnas',
    author_email = 'tho.ounn@gmail.com',
    url = 'https://github.com/thooun/pyblink',
    install_requires=[
        'argparse',
        'google-api-python-client',
    ],
    data_files=[('pyblink/image', ['pyblink/image/startup_script.sh'])],
    entry_points={
        'console_scripts': [
            'pyblink-build-image=pyblink.image.build_image:main',
            'pyblink-run=pyblink.run:main'
        ]
    }
)
