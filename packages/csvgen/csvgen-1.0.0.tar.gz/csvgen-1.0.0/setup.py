from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="csvgen",
    version="1.0.00",
    description="A command line CSV data output generator for testing",
    long_description=long_description,
    url="https://www.adamyork.com",
    license="MIT",
    author="Adam York",
    author_email="adam@adamyork.com",
    packages=find_packages(exclude=['contrib', 'tests*']),
    install_requires=[''],
    include_package_data=True,
    package_data={"data": ["all.last.txt", "cities.txt", "data_read_me.txt", "female.first.txt",
                  "male.first.txt", "places.txt", "suffixes.txt", "words.txt", "zip.codes.txt"],
                  "docs": ["help.txt", "man.txt"],
                  "output": ["output.txt", "readme.txt"]},
    project_urls={'AdamYork.com': 'https://www.adamyork.com', 'GitHub': 'https://github.com/yorkadam', },
    classifiers=[
        # How mature is this project? Common values are
        'Development Status :: 4 - Beta',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Topic :: Text Processing :: General',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3.6',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4', ],
    keywords='software development text processing testing',
    platforms=["LINUX", "UBUNTU 16+", "OSX 9+", "BSD", "WIN10"],
    python_requires='>=3',
    entry_points={
        'console_scripts': [
            'csvgen=csvgen.__main__:main',
        ],
    },
)
