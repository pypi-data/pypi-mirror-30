# -*- coding: utf-8 -*-
from __future__ import with_statement, print_function
import os
import sys
import platform
from setuptools import setup, find_packages

repo_base = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(repo_base, 'backports', 'range', 'README.rst')) as readme:
    long_description = readme.read()

cmdclass = {}
extensions = []

try:
    if platform.python_implementation() != 'CPython':
        raise NotImplementedError("No Cython support for %r implementation" % platform.python_implementation())
    import Cython.Distutils
    from distutils.extension import Extension
except Exception as err:
    print('Cannot cythonize "backports.range": %s' % err, file=sys.stderr)
else:
    source_base = os.path.join('backports', 'range')
    for basename in ('cyrange.pyx', 'cyrange_iterator.pyx'):
        rel_path = os.path.join(source_base, basename)
        for compiled_file in (os.path.splitext(rel_path)[0] + ext for ext in ('.so', '.c')):
            try:
                os.unlink(compiled_file)
            except OSError:
                pass
        mod_path = os.path.splitext(rel_path)[0].replace(os.sep, '.')
        extensions.append(
            Extension(name=mod_path, sources=[rel_path])
        )
    if extensions:
        cmdclass = {'build_ext': Cython.Distutils.build_ext}

#: restriction of compatible cython versions
Cython_Version = ''
if sys.version_info < (3, 3):
    Cython_Version += '<=0.26.1'

setup(
    name='backports.range',
    version='3.7.2',
    description='Backport of the python 3.X `range` class',
    long_description=long_description,
    author='Max Fischer',
    author_email='maxfischer2781@gmail.com',
    url='https://github.com/maxfischer2781/backports.range.git',
    license='MIT',
    namespace_packages=['backports'],
    extras_require={
        'cython': ['cython%s' % Cython_Version],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        ],
    keywords='backports range xrange',
    package_data={
        'backports':
            [
                'range/README.rst', 'range/LICENSE.txt',
                'range/*.pxd',
            ]
    },
    packages=find_packages(exclude=('backports_*',)),
    test_suite='backports_range_unittests',
    tests_require=['unittest2'],
    ext_modules=extensions,
    cmdclass=cmdclass,
)
