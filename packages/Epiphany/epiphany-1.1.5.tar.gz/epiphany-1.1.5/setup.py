from setuptools import setup

setup(
    name='epiphany',
    version='1.1.5',
    entry_points={
        'console_scripts': [
            'epiphany = epiphany.__main__:main'
        ]
    },
    url='http://github.com/br0kenb1nary/epiphany',
    license='MIT',
    author='Damien Rose',
    author_email='br0kenb1nary@users.noreply.github.com',
    install_requires=[
        'selenium>=3.11.0',
        'twine>=1.11.0'
    ],
    description='Epiphany'
)
