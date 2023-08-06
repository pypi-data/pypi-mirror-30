from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'requests>=2.18.4'
]

setup(
    name='gandyns',
    version='1.0.1',
    description='Update gandi DNS record with current public IP',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/r0x73/gandyns.git',
    author='Raphaël Santos',
    author_email='r@0x73.ch',
    classifiers=[
        'Environment :: Console',
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: End Users/Desktop',

        'Topic :: Internet :: Name Service (DNS)',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.6',
    ],
    keywords='dns gandi api',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': 'gandyns = gandyns.gandyns:main'
    },
)
