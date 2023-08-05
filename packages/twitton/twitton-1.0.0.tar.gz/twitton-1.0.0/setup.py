# coding=utf-8
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import twitton

requirements = open('requirements.pip').read().splitlines()

kw = dict(
    name = 'twitton',
    version = '1.0.0',
    description = 'A simple Data Scraping library for Twitter API',
    long_description = open('README.rst', 'r').read(),
    author = 'Marcos Vinícius Brás',
    author_email = 'marcosvbras@gmail.com',
    url = 'https://github.com/marcosvbras/twitton',
    download_url = 'https://github.com/marcosvbras/twitton',
    license='Apache',
    py_modules = ['twitton'],
    packages=['twitton'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='data twitter search scraping api',
    install_requires=requirements,
    python_requires='~=3.6',
)

setup(**kw)
