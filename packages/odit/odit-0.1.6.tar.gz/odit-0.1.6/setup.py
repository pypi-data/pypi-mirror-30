from setuptools import setup

setup(
    name='odit',
    version='0.1.6',
    packages=['odit'],
    install_requires=['azure', 'python-docx', 'PyYaml'],
    url='https://theecodedragon.com',
    license='Apache License 2.0',
    author='theecodedragon',
    author_email='theecodedragon@gmail.com',
    description='Document as code, This prototype is an example to show how build document can be generated '
                'programmatically ',
    entry_points={
        'console_scripts': ['odit=odit.cli:main'],
    }
)
