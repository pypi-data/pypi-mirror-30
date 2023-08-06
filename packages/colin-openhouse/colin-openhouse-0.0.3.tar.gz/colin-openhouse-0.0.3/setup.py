import os

from setuptools import setup, find_packages

BASE_PATH = os.path.dirname(__file__)

# https://packaging.python.org/guides/single-sourcing-package-version/
version = {}
with open("./colin-openhouse/version.py") as fp:
    exec(fp.read(), version)

long_description = ''.join(open('README.md').readlines())

setup(
    name='colin-openhouse',
    version=version["__version__"],
    description="Additional chceks for colin -- the container linter. Used for image building tutorial at Open House 2018.",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'colin',
    ],
    data_files=[("share/colin/rulesets/", ["rulesets/openhouse.json"])],
    license='GPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Utilities',
    ],
    keywords='containers,sanity,linter',
    author='Frantisek Lachman',
    author_email='flachman@redhat.com',
    url='https://github.com/lachmanfrantisek/colin-openhouse',)
