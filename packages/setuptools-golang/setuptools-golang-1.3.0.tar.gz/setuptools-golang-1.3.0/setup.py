from setuptools import setup


setup(
    name='setuptools-golang',
    description=(
        'A setuptools extension for building cpython extensions written in '
        'golang.'
    ),
    url='https://github.com/asottile/setuptools-golang',
    version='1.3.0',
    author='Anthony Sottile',
    author_email='asottile@umich.edu',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    py_modules=['setuptools_golang'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'setuptools-golang-build-manylinux-wheels = '
            'setuptools_golang:build_manylinux_wheels',
        ],
        'distutils.setup_keywords': [
            'build_golang = setuptools_golang:set_build_ext',
        ],
    },
)
