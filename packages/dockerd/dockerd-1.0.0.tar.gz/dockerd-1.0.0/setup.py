#!/bin/env python3
from setuptools import setup


with open('README.md') as f:
	readme = f.read()


setup(
	name='dockerd',
	version='1.0.0',
	description='Run Docker daemon as a subprocess',
	long_description=readme,
	author='Linus Lewandowski',
	author_email='linus@lew21.net',
	url='https://gitlab.com/lew21/dockerd-py',
	keywords='docker',

	packages=['dockerd'],
	include_package_data=True,

	zip_safe=True,
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Environment :: Other Environment',
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Topic :: Utilities',
		'License :: OSI Approved :: MIT License',
	]
)
