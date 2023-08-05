#!/usr/bin/python3

from setuptools import setup

home_page = 'https://github.com/luoyeah/netportal'

requires = [
    'requests>=2.18.4',
    'beautifulsoup4>=4.6.0',
    'docopt>=0.6.2',
    'PyExecJS>=1.5.1'
]

packages = [
    'netportal',
    'netportal.chinanet'
]

setup(
    name='netportal',
    version='1.1.5',
    keywords=(
        'netportal',
        'portal',
        'wifiman',
        'wifi',
        'cmccweb',
        'cmcc',
        'chinanet'
    ),
    author='luoyeah',
    author_email='luoyeah_ilku@foxmail.com',
    url=home_page,
    license='GPLv3',
    description='Network portal tools(CMCC, CMCC-WEB, ChinaNet...)',
    long_description='Detail: %s' % home_page,
    include_package_data=True,
    zip_safe=False,
    packages=packages,
    platforms='any',
    python_requires=">=3.0",
    install_requires=requires,
    entry_points={
        'console_scripts':[
            'netportal = netportal.netportal:main',
            'wifiman = netportal.wifiman:main',
            'cmccweb = netportal.cmccweb:main',
            'chinanet = netportal.chinanet.chinanet:main'
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
