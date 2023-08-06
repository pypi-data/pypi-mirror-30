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
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3',
		'Topic :: Text Processing :: Linguistic'
	],
	keywords = 'ASJP ASJPcode IPA',

	packages = find_packages(),
	package_data = {'asjp': ['data/*']},

	install_requires = ['ipatok >= 0.2'],
	python_requires = '>=3',

	test_suite = 'asjp.tests',
	tests_require = ['hypothesis >= 3.52']
)
