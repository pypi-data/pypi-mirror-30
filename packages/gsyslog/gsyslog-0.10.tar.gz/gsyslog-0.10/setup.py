#!/usr/bin/python


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def readme(filespec):
    """Utility to return readme contents for long description"""
    with open(filespec) as f:
        return f.read()


setup(
    name='gsyslog',
    version='0.10',
    packages=['gsyslog'],
    description='George application logger similar to syslog',
    long_description=readme('README.md'),
    keywords='log logger logging gsyslog syslog',
    author='George L Fulk',
    author_email='fulkgl@gmail.com',
    url='https://github.com/fulkgl/gsyslog',
    scripts=[],
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
