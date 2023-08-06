from setuptools import setup, find_packages


setup(
    name="tonglei",
    version="0.1.0",
    author="Leo Tong",
    author_email="tonglei@qq.com",
    description="tonglei",
    long_description=open("README.rst").read(),
    license="Apache License, Version 2.0",
    url="https://github.com/tonglei100/tonglei",
    packages=['tonglei'],
    package_data={'tonglei': ['*.py']},
    install_requires=[
        'xlrd',
        'xlsxwriter'
        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.6"
    ],
    entry_points={

    }
)
