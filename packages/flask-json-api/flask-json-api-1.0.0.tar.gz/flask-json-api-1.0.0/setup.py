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


__version__ = find_version("flask_json_api/__init__.py")


def read(filename):
    with open(filename) as fp:
        content = fp.read()
    return content


setup(
    name='flask-json-api',
    version=__version__,
    description=['The Flask JSON API package provides boilerplate code '
                 'for setting up REST based apps.'],
    long_description=read('README.rst'),
    author='Victor Klapholz',
    author_email='victor.klapholz@gmail.com',
    url='https://gitlab.com/py-ddd/flask-json-api',
    packages=['flask_json_api'],
    include_package_data=True,
    license='MIT',
    install_requires=[
        'flask>=0.12.2',
    ],
    zip_safe=False,
    keywords=[
        'flask', 'rest', 'json', 'api', 'content-type', 'exception'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    test_suite='tests'
)
