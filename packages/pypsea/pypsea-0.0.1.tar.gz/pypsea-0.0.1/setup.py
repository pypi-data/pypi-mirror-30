"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
https://github.com/genepattern/genepattern-notebook/blob/master/setup.py
"""
import os
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop


here = os.getcwd()

# with open(os.path.join(here, 'pypsea', '__version__')) as f:
#     __version__ = f.read().strip()

__version__ = "0.0.1"

# FIXME: FINISH THIS!!!

# is_windows = False
is_windows = os.name == "nt"

if is_windows:
    os_where = 'where {}'
else:
    os_where = 'whereis {}'



def _post_install():
    """After installing the python module enable the nbextensions.
    """
    import subprocess
    from distutils import log
    log.set_verbosity(log.DEBUG)

    try:
        subprocess.call(["conda", "install", "-c", "cyclus", "java-jdk"])
        # COMPILE PSEAQuant with javac

    except:
        log.warn("Consider this your first warning.")


class pypseaInstall(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, [], msg="Running post install task")


class pypseaDevelop(_develop):
    def run(self):
        _develop.run(self)
        self.execute(_post_install, [], msg="Running post develop task")


setup(
    name='pypsea',
    version=__version__,
    description="Protein Set Enrichment Analysis (PSEA) in a Python wrapper.",
    # The project's main homepage.
    url='https://github.com/draperjames/pypsea',
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

    keywords='Jupyter Notebook',
    packages=find_packages(),
    package_data = {'pypsea': ['__version__', 'fileupload/static/*.js'],},
    install_requires=['pandas', 'xlrd'],
    cmdclass={'install': pypseaInstall, "develop":pypseaDevelop},

    # entry_points={
    #     'console_scripts': [
    #         'pypsea=pypsea:main'
    #         #'sample=sample:main',
    #     ],
    # },
)
