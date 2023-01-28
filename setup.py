
from setuptools import setup, find_packages

with open( 'README.md', 'r', encoding='utf-8' ) as fh:
	README = fh.read()

setuptools.setup(
	name='omada-api',
	version='5.7.4',
	description='A simple Python wrapper for the TP-Link Omada Software Controller API',
	long_description=README,
	long_description_content_type='text/markdown',
	url='https://ghaberek.github.io/omada-api',
	author='Gregory Haberek',
	author_email='ghaberek@gmail.com',
	license='MIT',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3.7',
		'Topic :: Software Development :: Libraries',
	],
	keywords='tplink omada wrapper',
	project_urls={
		'Source': 'https://github.com/ghaberek/omada-api',
		'Issues': 'https://github.com/ghaberek/omada-api/issues',
		'Wiki': 'https://github.com/ghaberek/omada-api/wiki',
	},
	packages=find_packages(),
	install_requires=[
		'requests>=2.28.0'
	],
	python_requires='>=3.7',
)
