from setuptools import setup

import re


version = ''
with open('cuckoo/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Version is not set')


readme = 'See https://github.com/opfront/cuckoo for details.'

with open('requirements.txt', 'r') as infile:
    requirements = infile.readlines() 


setup(
    name='cuckoo-db',
    version='0.1.0',
    packages=['cuckoo'],
    license='MIT',
    author='opfront',
    author_email='dalloriam@gmail.com',
    url='https://github.com/opfront/cuckoo',
    description='Simple migration tool',
    long_description=readme,
    entry_points={
        'console_scripts': [
            'cuckoo=cuckoo.__main__:main'
        ]
    },
    install_requires=requirements
)