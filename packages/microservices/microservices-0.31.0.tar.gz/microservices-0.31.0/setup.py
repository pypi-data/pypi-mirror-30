import os
from distutils.core import setup
from setuptools import find_packages

package = 'microservices'

version = __import__(package).get_version()
packages = find_packages()


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


setup(
    name=package,
    version=version,
    packages=packages,
    package_data=get_package_data(package),
    license='MIT',
    author='viatoriche',
    author_email='maxim@via-net.org',
    description='Microservices builder',
    url='https://github.com/viatoriche/microservices',
    download_url='https://github.com/viatoriche/microservices/tarball/{}'.format(
        version),
    install_requires=[
        'Flask-API==1.1.b1', 'requests>=2.10.0',
        'six', 'Markdown==2.6.6', 'kombu==4.1.0'
    ],
)
