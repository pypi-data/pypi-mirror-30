from setuptools import find_packages
from setuptools import setup


VERSION = '0.8.2'

setup(
    name='detect_secrets',
    packages=find_packages(exclude=(['test*', 'tmp*'])),
    version=VERSION,
    description='Tool for detecting secrets in the codebase',
    long_description="Check out detect-secrets on `GitHub <https://github.com/Yelp/detect-secrets>`_!",
    license="Copyright Yelp, Inc. 2018",
    author='Aaron Loo',
    author_email='aaronloo@yelp.com',
    url='https://github.com/Yelp/detect-secrets',
    download_url='https://github.com/Yelp/detect-secrets/archive/{}.tar.gz'.format(VERSION),
    keywords=['secret-management', 'pre-commit', 'security', 'entropy-checks'],
    install_requires=[
        'enum34',
        'future',
        'pyyaml',
        'unidiff',
    ],
    entry_points={
        'console_scripts': [
            'detect-secrets = detect_secrets.main:main',
            'detect-secrets-hook = detect_secrets.pre_commit_hook:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Utilities",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
    ]
)
