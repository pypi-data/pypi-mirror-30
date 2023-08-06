from setuptools import setup

setup(name='testo',
	version='0.0.2',
	description='CI framework',
	url='https://github.com/log0div0/testo',
	author='Sergey Lvov',
	author_email='log0div0@gmail.com',
	license='MIT',
	packages=['testo'],
	zip_safe=False,
	entry_points={
		'console_scripts': [
			'testo=testo:joke',
		],
	})
