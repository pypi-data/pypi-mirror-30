#!/usr/bin/env python
"""Defines the setup instructions for falcon_middleware_beaker"""
import glob
import os
import sys
from os import path

from setuptools import Extension, setup
from setuptools.command.test import test as TestCommand

MYDIR = path.abspath(os.path.dirname(__file__))
JYTHON = 'java' in sys.platform
PYPY = bool(getattr(sys, 'pypy_version_info', False))
CYTHON = False
if not PYPY and not JYTHON:
    try:
        from Cython.Distutils import build_ext
        CYTHON = True
    except ImportError:
        pass

cmdclass = {}
ext_modules = []
if CYTHON:
    def list_modules(dirname):
        filenames = glob.glob(path.join(dirname, '*.py'))

        module_names = []
        for name in filenames:
            module, ext = path.splitext(path.basename(name))
            if module != '__init__':
                module_names.append(module)

        return module_names

    ext_modules = [
        Extension('falcon_middleware_beaker.' + ext, [path.join('falcon_middleware_beaker', ext + '.py')])
        for ext in list_modules(path.join(MYDIR, 'falcon_middleware_beaker'))]
    cmdclass['build_ext'] = build_ext


class PyTest(TestCommand):
    extra_kwargs = {'tests_require': ['pytest', 'mock']}

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


cmdclass['test'] = PyTest

try:
    import pypandoc
    readme = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, OSError, RuntimeError):
    readme = ''

setup(name='falcon_middleware_beaker',
      version='0.0.1',
      description='Beaker integration for falcon / hug',
      long_description=readme,
      author='Maciej Baranski',
      author_email='maciej.baranski.gtxm@gmail.com',
      url='https://github.com/gtxm/falcon_middleware_beaker',
      license="MIT",
      packages=['falcon_middleware_beaker'],
      requires=[],
      install_requires=['falcon'],
      cmdclass=cmdclass,
      ext_modules=ext_modules,
      keywords='Python, Python3, falcon, hug',
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
                   'Topic :: Utilities'],
      **PyTest.extra_kwargs)
