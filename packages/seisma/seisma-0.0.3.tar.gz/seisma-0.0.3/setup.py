# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


__version__ = '0.0.3'


def install_package():
    setup(
        name='seisma',
        version=__version__,
        url='https://github.com/trifonovmixail/seisma-client',
        packages=find_packages(exclude=('tests*',)),
        author='Mikhail Trifonov',
        author_email='trifonovmixail@ya.ru',
        license='GNU LGPL',
        description='Python binding to seisma analytic system',
        keywords='client rest binding',
        long_description=open('README.rst').read(),
        include_package_data=True,
        zip_safe=False,
        platforms='any',
        install_requires=['requests>=2.5'],
        classifiers=(
            'Development Status :: 3 - Alpha',
            'Natural Language :: Russian',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: Implementation :: CPython',
            'Topic :: Software Development :: Testing',
        ),
    )


if __name__ == '__main__':
    install_package()
