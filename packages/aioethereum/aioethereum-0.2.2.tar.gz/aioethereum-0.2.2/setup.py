import re
import os.path
import sys
import platform
from setuptools import setup, find_packages


uvloop = 'uvloop>=0.8.1'
install_requires = [
    'aiohttp>=2.2.5',
    'async-timeout>=1.4.0',
]
if platform.python_implementation() == 'CPython':
    install_requires.append('ujson')

PY_VER = sys.version_info

if PY_VER >= (3, 5) and sys.platform != "win32":
    install_requires.append(uvloop)
elif PY_VER >= (3, 4):
    pass
elif PY_VER >= (3, 3):
    install_requires.append('asyncio>=3.4.3')
else:
    raise RuntimeError("aioethereum doesn't support Python version prior 3.3")


def read(*parts):
    with open(os.path.join(*parts), 'rt') as f:
        return f.read().strip()


def read_version():
    regexp = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")
    init_py = os.path.join(os.path.dirname(__file__),
                           'aioethereum', '__init__.py')
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        else:
            raise RuntimeError('Cannot find version in '
                               'aioethereum/__init__.py')


classifiers = [
    'License :: OSI Approved :: MIT License',
    'Development Status :: 4 - Beta',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Operating System :: POSIX',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
    'Framework :: AsyncIO',
]

setup(
    name='aioethereum',
    version=read_version(),
    description=("Ethereum RPC client library for Python asyncio (PEP 3156)"),
    long_description="\n\n".join((read('README.rst'), read('CHANGES.rst'))),
    classifiers=classifiers,
    platforms=["POSIX"],
    author="Bogdan Kurinnyi",
    author_email="bogdankurinniy.dev1@gmail.com",
    url="https://github.com/DeV1doR/aioethereum",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    install_requires=install_requires,
    include_package_data=True,
)
