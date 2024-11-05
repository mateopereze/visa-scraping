from setuptools import setup, find_packages
from os.path import splitext, basename
import versioneer

setup(
    name = 'visa_scraping',
    author = 'mateopereze',
    author_email = 'mateo.pereze4@gmail.com',
    description = 'Este proyecto se centra en la recolección automatizada de información a través de técnicas de web scraping.',
    license = '...',
    url = 'https://github.com/mateopereze/visa_scraping',
    package_dir={'': 'src'},
    python_requires = '>=3.11',
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(where='src'),
    install_requires = [
        'openpyxl>=3.1.2',
        'pandas>=2.2.3',
        'beautifulsoup4>=4.12.3',
        'selenium>=4.25.0'
    ]
)
