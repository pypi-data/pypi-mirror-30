"""
pyhector
--------

Python wrapper for the `Hector simple climate model
<https://github.com/JGCRI/hector>`_.

**Install** using ::

    pip install pyhector

Find **usage** instructions in the `repository
<https://github.com/openclimatedata/pyhector>`_.

"""
from setuptools import setup, Extension
from setuptools.command.test import test as TestCommand
import glob
import sys
import versioneer


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


cmdclass = versioneer.get_cmdclass()
cmdclass.update({"test": PyTest})

libpyhector = Extension(
    'libpyhector',
    include_dirs=[
        'hector-wrapper/include',
        'hector-wrapper/hector/headers'
    ],
    libraries=['m', 'boost_system', 'boost_filesystem'],
    extra_compile_args=['-std=c++11'],
    sources=(glob.glob('src/*.cpp') +
             glob.glob('hector-wrapper/src/*.cpp') +
             glob.glob('hector-wrapper/hector/source/core/*.cpp') +
             glob.glob('hector-wrapper/hector/source/models/*.cpp') +
             glob.glob('hector-wrapper/hector/source/components/*.cpp') +
             glob.glob('hector-wrapper/hector/source/data/*.cpp')),
    depends=(glob.glob('hector-wrapper/include/*.h') +
             glob.glob('hector-wrapper/hector/headers/**/*.hpp'))
)

setup(
    name='pyhector',
    version=versioneer.get_version(),
    cmdclass=cmdclass,
    description='Python wrapper for the Hector simple climate model',
    long_description=__doc__,
    url='https://github.com/openclimatedata/pyhector',
    author='Sven Willner, Robert Gieseke',
    author_email='sven.willner@pik-potsdam.de, robert.gieseke@pik-potsdam.de',
    license='GNU Affero General Public License v3',
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='',
    package_data={'pyhector': ['rcp_default.ini', 'emissions/*']},
    include_package_data=True,
    packages=['pyhector'],
    install_requires=['pandas', 'numpy'],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    ext_modules=[libpyhector]
)
