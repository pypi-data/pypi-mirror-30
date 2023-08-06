# -*- coding: utf-8 -*-

"""
	Adapted from https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
"""

from setuptools import setup


with open('README.rst', 'r') as fh:
	readme = fh.read()

setup(
	name='django_hreflang',  # should have used a - sorry
	description='Generate the hreflang html header lines when using i18n urls on Django sites',
	long_description=readme,
	url='https://bitbucket.org/mverleg/django_hreflang',
	author='Mark V',
	maintainer='(the author)',
	author_email='mdilligaf@gmail.com',
	license='Revised BSD License (LICENSE.txt)',
	keywords=['django', 'hreflang', 'http-headers', 'internationalization'],
	version='2.1',
	packages=['hreflang', 'hreflang.templatetags'],
	include_package_data=True,
	zip_safe=False,
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: Implementation :: PyPy',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
	install_requires= ['django>=2.0']
)


