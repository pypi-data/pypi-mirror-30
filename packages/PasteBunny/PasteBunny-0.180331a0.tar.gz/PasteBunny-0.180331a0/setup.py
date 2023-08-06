from __future__ import with_statement
import re
import codecs

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

# detect the current version
with open('PasteBunny/__init__.py') as f:
    version = re.search(r'__version__\s*=\s*\'(.+?)\'', f.read()).group(1)
assert version

with codecs.open('README.md', 'r', encoding='utf8') as f:
    setup(
        name='PasteBunny',
        packages=['PasteBunny'],
        version=version,
        description='Pastebin wrapper made by bunnies, for bunnies...',
        long_description=f.read(),
        license='Bunny Licensse',
        author='BUNNY TMJ',
        author_email='tmukkuroj1337@gmail.com',
        url='https://github.com/tmjvonboss/PasteBunny.git',
        keywords=['PasteBunny'],
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
        ],
        install_requires=[
            'requests',
            'aiohttp',
            'aiodns',
            'cchardet',
            'asyncio'
        ],
    )