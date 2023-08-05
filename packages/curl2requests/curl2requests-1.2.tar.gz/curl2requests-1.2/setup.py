import codecs
from setuptools import setup

with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'curl2requests',
    version = '1.2',
    license='GPL',
    description = 'parse cURL command and return JSON data',
    author = 'mark0smith',
    author_email = 'm11711237@gmail.com',

    url = 'https://github.com/a4m/curl2requests',
    packages = ['curl2requests'], 
    package_data={
        'curl2requests': ['README.rst', 'LICENSE']
    },
    download_url = 'https://github.com/a4m/curl2requests/archive/1.1.tar.gz', 
    keywords = ['cURL', 'requests'], # arbitrary keywords
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
    ],
    entry_points="""
    [console_scripts]
    curl2req = curl2requests.curl2requests:main
    """,

    long_description=long_description,
)
