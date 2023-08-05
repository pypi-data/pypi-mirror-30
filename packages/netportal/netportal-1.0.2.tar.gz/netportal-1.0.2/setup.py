#!/usr/bin/python3

from setuptools import setup

home_page = 'https://github.com/luoyeah/netportal'

requires = [
    'requests>=2.18.4',
    'beautifulsoup4>=4.6.0',
    'docopt>=0.6.2'
]

packages = [
    'netportal'
]

setup(
    name='netportal',
    version='1.0.2',
    keywords=(
        'netportal',
        'portal',
        'cmccweb',
        'cmcc'
    ),
    author='luoyeah',
    author_email='luoyeah_ilku@foxmail.com',
    url=home_page,
    license='GPLv3',
    description='Network website portal tools.',
    long_description='HomePage: %s' % home_page,
    include_package_data=True,
    zip_safe=False,
    packages=packages,
    platforms='any',
    python_requires=">=3.0",
    install_requires=requires,
    entry_points={
        'console_scripts':[
            'cmccweb = netportal.cmccweb:main'
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
