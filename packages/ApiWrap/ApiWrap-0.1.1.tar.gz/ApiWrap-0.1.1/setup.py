from setuptools import setup, find_packages

setup(
    name = 'ApiWrap',
    version = '0.1.1',
    description = 'A simple HTTP POST API wrapper for Python classes',
    author = 'George A. Mihaila',
    author_email = 'george.mihaila@gmail.com',
    license = 'MIT',
    url = 'https://github.com/gamihaila/ApiWrap',
    download_url = 'https://github.com/gamihaila/ApiWrap/archive/0.1.1.tar.gz',
    packages=['wrapit'],
    install_requires=[
        "Flask"
    ],
    classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    # Pick your license as you wish (should match "license" above)
     'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3.4',
],
)
