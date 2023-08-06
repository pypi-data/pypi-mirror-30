from setuptools import setup, find_packages

setup(
	name="xswitch",
	version="1.0.3",
	packages=find_packages(),
	description="My usefull functions",
	url="https://0xswitch.fr",
	author="switch",
	license="WTFPL",
	python_requires=">=2.7",
	install_requires=[""],

	entry_points = {
        'console_scripts': [
            'x_pattern = xswitch.xswitch:x_pattern',
        ],
    }

	)