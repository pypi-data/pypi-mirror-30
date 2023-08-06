from setuptools import setup

setup(
	name='pydeployer',
    version='0.1.1',
    description='Python toolkit for deploying local project to a remote server.',
    url='https://github.com/jkuijt/pydeployer',
    author='Jasper Kuijt',
    author_email='jasperkuijt@live.nl',
    license='MIT',
    packages=['pydeployer'],
    zip_safe=True,
	classifiers=[
		'Programming Language :: Python'
	],
    entry_points={
        'console_scripts': [
            'pydeployer = pydeployer.__main__:main',
        ],
    },
	install_requires=['passlib','cryptography'],
)  