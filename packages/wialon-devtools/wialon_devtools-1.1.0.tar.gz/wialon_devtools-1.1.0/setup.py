from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.txt'), encoding='utf-8') as f:
	long_description = f.read()

setup(
	name='wialon_devtools',
	version='1.1.0',
	description='Wialon Devtools',
	long_description=long_description,
	url='https://github.com/shevast/wialon_devtools',
	author='Sergey Shevchik',
	author_email='sergey.shevchik@gmail.com',
	packages=find_packages(),
    install_requires=['pyqt5', 'pycrc', 'appdirs', 'setuptools'],
	package_data={
        '': ['presets/*.preset', 'images/*.png']
    },

	entry_points={
		'gui_scripts': [
			'wialon_devtools=wdt:run',
		],
	}
)
