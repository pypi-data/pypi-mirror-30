#!/usr/bin/python3

from setuptools import setup

home_page = 'https://github.com/luoyeah/alidns'

requires = [
    'aliyun-python-sdk-core-v3>=2.5.2',
    'aliyun-python-sdk-alidns>=2.0.7'
]

packages = [
    'alidns'
]

setup(
    name='alidns',
    version='1.0.5',
    keywords=(
        'alidns',
        'aliyun',
        'ddns'
    ),
    author='luoyeah',
    author_email='luoyeah_ilku@foxmail.com',
    url=home_page,
    license='GPLv3',
    description='Aliyun-DNS update tool.',
    long_description='HomePage: %s' % home_page,
    include_package_data=True,
    zip_safe=False,
    packages=packages,
    platforms='any',
    python_requires=">=3.0",
    install_requires=requires,
    entry_points={
        'console_scripts':[
            'alidns = alidns.alidns:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
