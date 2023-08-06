from setuptools import setup, find_packages

setup(
    name='genius-cli',
    version='1.0.7',
    packages=find_packages(),

    url='',
    license='Private',
    author='Alex Rudakov',
    author_email='alex@negative.ee',
    description='Genius generator.',
    long_description='',

    install_requires=[
        "termcolor",
        'click',
        'jinja2',
        'requests'
    ],

    entry_points={
        'console_scripts': [
            'genius = genius_cli.main:run',
        ]
    },
)

