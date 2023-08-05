# -*- coding:utf-8 -*-
from os.path import dirname, join
from setuptools import find_packages
from distutils.core import setup

# with open(join(dirname(__file__), 'cnrpc/VERSION'), 'rb') as f:
#     version = f.read().decode('ascii').strip()
version = __import__("cnrpc").__version__

extras_require = {}

setup(
    name='cnrpc',
    version=version,
    url='http://moha.vip',
    description='Simple rpc module in computer network lesson',
    long_description=open('README.rst').read(),
    author='Tim Kong',
    maintainer='Tim Kong',
    maintainer_email='yjxkwp@foxmail.com',
    license='BSD',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
    ],
    extras_require=extras_require,
)
