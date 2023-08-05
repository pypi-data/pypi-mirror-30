#!/usr/bin/env python3

from setuptools import setup, Extension, Command

import os 

config = {
    'libraries': [ 'clang' ],
    'extra_compile_args': [ '-std=c++11', '-Werror' ],
    'sources': [
        'src/teager.cpp',
        'src/Parser.cpp',
    ],
    'include_dirs': [ 'inc' ],
}

llvm = os.environ.get('PATH_TO_LLVM')
if llvm:
    config['include_dirs'] += [ os.path.join(llvm, 'include') ]
    config['library_dirs'] =  [ os.path.join(llvm, 'lib') ]

teager = Extension('teager', **config)

class TestCommand(Command):
    """
    Execute unit tests
    """
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import os
        import sys
        import unittest

        # get setup.py directory
        setup_file = sys.modules['__main__'].__file__
        setup_dir = os.path.abspath(os.path.dirname(setup_file))

        # use the default shared TestLoader instance
        test_loader = unittest.defaultTestLoader

        # use the basic test runner that outputs to sys.stderr
        test_runner = unittest.TextTestRunner()

        # automatically discover all tests
        test_suite = test_loader.discover(setup_dir)

        # run the test suite
        test_runner.run(test_suite)

setup(
    name='teager',
    version='0.1.1',
    description='AST traversal powered by libclang',
    long_description_type='text/markdown',
    author='Jem Tucker',
    author_email='mail@jemtucker.com',
    url='https://github.com/jemtucker/teager',
    ext_modules=[
        teager,
    ],
    cmdclass={ 
        'test': TestCommand,
    }, 
    license='GNUv3',
    python_requires='>=3',
    classifiers={
        # Currently unstable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
    })



