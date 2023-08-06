"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))
bindir = os.path.join(here, "bin/")

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
	long_description = f.read()

setup(name='ggc',
	version='0.0.1',
	description='''Basic methods, for common usage across packages''',
	long_description=long_description,
	url='https://github.com/ggirelli/ggc',
	long_description_content_type='text/markdown',
	author='Gabriele Girelli',
	author_email='gabriele.girelli@scilifelab.se',
	license='MIT',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering :: Bio-Informatics',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3 :: Only',
	],
	keywords='common',
	packages=find_packages(),
	install_requires=["biopython", "tqdm"],
	scripts=[],
	test_suite="nose.collector",
	tests_require=["nose"],
)
