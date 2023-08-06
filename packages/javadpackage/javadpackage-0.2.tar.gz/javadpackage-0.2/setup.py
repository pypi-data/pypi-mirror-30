from setuptools import setup, find_packages

setup(
	name='javadpackage',
	packages=find_packages(),
	version='0.2',
	description='this is my first python package - version 2',
	author='javad mokhtari',
	author_email='javadmokhtari@outlook.com',
	url='http://javadmko.ir',
	keywords=['sample python package'],
	entry_points={
				'console_scripts': [
					'jlow = mypackage.demo:demoprint'
				]
			}
)

