#!/usr/bin/env python

from    setuptools import setup
import  os

package_name = "ROPgadget4ROPGenerator"
package_dir  = "ropgadget4ropgenerator"
package_description = """
This is a python package of the famous ROPgadget tool version 5.6 used to support the ROPGenerator tool
This package was created because the ROPgadget pypi package is obsolete and no later version has or seems to be going to be uploaded soon
More infos about ROPgadget can be found at : http://www.shell-storm.org/project/ROPgadget/
""".strip()


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk(package_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

version = "5.6.1"

setup(
    name             = package_name,
    version          = version,
    description      = package_description,
    packages         = packages,
    license          = "BSD",
    author           = "Jonathan Salwan",
    author_email     = "jonathan.salwan@gmail.com",
    url              = "https://github.com/JonathanSalwan/ROPgadget",
    scripts          = ['scripts/ROPgadget4ROPGenerator'],
    classifiers      = [
        'Topic :: Security',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers'
    ]
)
