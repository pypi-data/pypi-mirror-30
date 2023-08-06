#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# To generate DEB package from Python Package:
# sudo pip3 install stdeb
# python3 setup.py --verbose --command-packages=stdeb.command bdist_deb
#
#
# To generate RPM package from Python Package:
# sudo apt-get install rpm
# python3 setup.py bdist_rpm --verbose --fix-python --binary-only
#
#
# To generate EXE MS Windows from Python Package (from MS Windows only):
# python3 setup.py bdist_wininst --verbose
#
#
# To generate PKGBUILD ArchLinux from Python Package (from PyPI only):
# sudo pip3 install git+https://github.com/bluepeppers/pip2arch.git
# pip2arch.py PackageNameHere
#
#
# To Upload to PyPI by executing:
# python3 setup.py register
# python3 setup.py bdist_egg sdist --formats=zip upload --sign


from setuptools import setup, Command
from zipapp import create_archive


class ZipApp(Command):
    description, user_options = "Creates a zipapp.", []

    def initialize_options(self): pass  # Dont needed, but required.

    def finalize_options(self): pass  # Dont needed, but required.

    def run(self):
        return create_archive("css-html-prettify.py", "css-html-prettify.pyz",
                              "/usr/bin/env python3")


setup(
    requires=['anglerfish', 'beautifulsoup4'],
    scripts=["css-html-prettify.py"],
    cmdclass={"zipapp": ZipApp},
)
