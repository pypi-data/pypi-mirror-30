import re
from setuptools import setup


def find_version(filename):
    """Attempts to find the version number in the file names filename.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(filename, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


__version__ = find_version("toastedmarshmallow_enum/__init__.py")


def read(filename):
    with open(filename) as fp:
        content = fp.read()
    return content


setup(
    name='toastedmarshmallow-enum',
    version=__version__,
    description=['The Toasted Marshmallow Enum package makes it possible '
                 'to dump and load Enum values based on the ultra fast '
                 'serialization that Toasted Marshmallow provides.'],
    long_description=read('README.rst'),
    author='Victor Klapholz',
    author_email='victor.klapholz@gmail.com',
    url='https://gitlab.com/py-ddd/toastedmarshmallow-enum',
    packages=['toastedmarshmallow_enum'],
    include_package_data=True,
    license='apache2',
    install_requires=[
        'toastedmarshmallow',
        'six'
    ],
    zip_safe=False,
    keywords=[
        'serialization', 'rest', 'json', 'api', 'marshal',
        'marshalling', 'deserialization', 'validation', 'schema',
        'toastedmarshmallow', 'enum'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    test_suite='tests'
)
