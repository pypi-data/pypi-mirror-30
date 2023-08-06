import re

from setuptools import setup


version = None
version_re = re.compile(r"__version__ = '(.*)'")

with open('okta_uuid.py') as f:
    buf = f.read()
    m = version_re.search(buf)
    version = m.group(1)

if not version:
    raise RuntimeError('could not find version in okta_uuid.py, aborting')

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='okta-uuid',
    version=version,
    description='Turn Okta User IDs into UUIDs.',
    long_description=long_description,
    author='Travis Mehlinger',
    author_email='tmehlinger@gmail.com',
    url='https://github.com/tmehlinger/okta-uuid',
    py_modules=['okta_uuid'],
    install_requires=['pybase62'],
    license='MIT',
    keywords='okta uuid',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
