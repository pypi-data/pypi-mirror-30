#!/usr/bin/python3 -S
import os
import uuid
from setuptools import setup, Extension
from pip.req import parse_requirements
from pkgutil import walk_packages
from Cython.Build import cythonize
from distutils.command.build_ext import build_ext

pathname = os.path.dirname(os.path.realpath(__file__))


PKG = 'kola'
PKG_NAME = 'kola-bottle'
PKG_VERSION = '0.1.1'


# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(pathname + "/requirements.txt",
                                  session=uuid.uuid1())


def find_packages(prefix=""):
    path = [prefix]
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name


class _build_ext(build_ext):
    def run(self):
        build_ext.run(self)

    def build_extension(self, ext):
        build_ext.build_extension(self, ext)


# Cythonizes MultiDict
extensions = cythonize([
    Extension('kola.multidict', [pathname + '/kola/multidict.pyx'])])


setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    description='A WSGI framework for Python 3 based upon Bottle.',
    author='Jared Lunde',
    author_email='jared.lunde@gmail.com',
    url='https://github.com/jaredlunde/kola',
    license="MIT",
    install_requires=[str(ir.req) for ir in install_reqs],
    packages=list(find_packages(PKG)),
    ext_modules=extensions,
    cmdclass=dict(build_ext=_build_ext)
)
