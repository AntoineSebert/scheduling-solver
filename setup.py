from distutils.core import setup as core_setup
from Cython.Build import cythonize
from setuptools import setup, find_packages

setup(
	name="Scheduling Solver",
	version="0.2.0-alpha",
	packages=find_packages(),
	scripts=['say_hello.py'],

	# Project uses reStructuredText, so ensure that the docutils get
	# installed or upgraded on the target machine
	install_requires=['docutils>=0.3'],

	python_requires="3.6",
	package_dir={'': 'src'},
	test_suite='your.module.tests',

	# metadata to display on PyPI
	author="Antoine Sébert",
	author_email="antoine.sb@orange.fr",
	description="This is an Example Package",
	keywords="hello world example examples",
	url="http://example.com/HelloWorld/",   # project home page, if any
	project_urls={
		"Bug Tracker": "https://bugs.example.com/HelloWorld/",
		"Documentation": "https://docs.example.com/HelloWorld/",
		"Source Code": "https://code.example.com/HelloWorld/",
	},
	classifiers=[
		'License :: OSI Approved :: Python Software Foundation License'
	],
	ext_modules=cythonize("hello.pyx")

	# could also include long_description, download_url, etc.
)
