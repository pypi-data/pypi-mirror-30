import os.path

from setuptools import setup, find_packages



BASE_DIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(BASE_DIR, 'README.rst')) as f:
	README = f.read()

with open(os.path.join(BASE_DIR, 'asjp/__version__.py')) as f:
	exec(f.read())



setup(
	name = 'asjp',
	version = VERSION,

	description = 'ASJP conversion and tokenisation utils',
	long_description = README,

	url = 'https://github.com/pavelsof/asjp',

	author = 'Pavel Sofroniev',
	author_email = 'pavelsof@gmail.com',

	license = 'MIT',

	classifiers = [
		'Development Status :: 1 - Planning',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3',
		'Topic :: Text Processing :: Linguistic'
	],
	keywords = 'ASJP ASJPcode IPA',

	packages = find_packages(),
	package_data = {'asjp': ['data/*']},

	install_requires = [],

	test_suite = 'asjp.tests'
)
