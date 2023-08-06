"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

setup(
    name='plex-pre-transcode',
    packages=['plex-pre-transcode'],
    version='0.1.6',
    python_requires='>=3',
    description='Pre transcode Plex videos.',
    author='Martino Jones',
    author_email='martino@martinojones.com',
    url='https://github.com/martinoj2009/plex-pre-transcode',
    download_url='https://github.com/martinoj2009/plex-pre-transcode',
    keywords=['plex', 'emby', 'transcode'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    project_urls={
        'Source': 'https://github.com/martinoj2009/plex-pre-transcode',
    },
    scripts=['plex-pre-transcode/plex-pre-transcode.py'],
)
