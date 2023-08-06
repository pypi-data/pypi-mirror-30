import os
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop


here = os.getcwd()

with open(os.path.join(here, 'forgit', '__version__')) as f:
    __version__ = f.read().strip()


def _post_install():
    """After installing the python module enable the nbextensions.

    Inspired by https://github.com/genepattern/genepattern-notebook/blob/master/setup.py.
    """
    import subprocess
    from distutils import log
    log.set_verbosity(log.DEBUG)

    try:
        print("Downloading most resent gitignores from Github.com...")
        pass
    except:
        log.warn("Post Install Failed.")
        pass


class ForgitInstall(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, [], msg="Running post install task")


class ForgitDevelop(_develop):
    def run(self):
        _develop.run(self)
        self.execute(_post_install, [], msg="Running post develop task")


setup(
    name='forgit',
    version=__version__,
    description="Tools for git and github",
    # The project's main homepage.
    url='https://github.com/draperjames/forgit',
    # Author details
    author='James Draper',
    author_email='james.draper@duke.edu',
    # Choose your license
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='Git',
    packages=find_packages(),
    package_data = {'forgit': ['__version__',],},
    # install_requires=['pandas', 'xlrd'],
    cmdclass={'install': ForgitInstall, "develop":ForgitDevelop},
    # Set the console entry point.
    entry_points={
        'console_scripts': [
            'forgit=forgit:main.main'
        ],
    },
)
