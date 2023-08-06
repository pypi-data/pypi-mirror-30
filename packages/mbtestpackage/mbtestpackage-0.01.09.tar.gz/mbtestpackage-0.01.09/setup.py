import atexit
import os
import sys
from setuptools import setup
from setuptools.command.install import install
my_name='mbtestpackage'
class CustomInstall(install):
    def run(self):
        def _post_install():
            def find_module_path():
                for p in sys.path:
                    if os.path.isdir(p) and my_name in os.listdir(p):
                        return os.path.join(p, my_name)
            install_path = find_module_path()

            # Add your post install code here

        atexit.register(_post_install)
        install.run(self)

from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        print("hello mama")
        install.run(self)

setup(
    name='mbtestpackage',
    version='0.01.09',
    author='Alectryon LLC',
    author_email='mbiedler@gmail.com',
    packages=['mbtestpackage', 'mbtestpackage.test'],
    url='http://pypi.python.org/pypi/mbtestpackage/',
    install_requires=[
        'Click',
    ],
    entry_points = {
        'console_scripts': ['myprogram=mbtestpackage.command_line:main','myprogram3=mbtestpackage.command_line:startup'],
    },
    cmdclass={        
        'install': CustomInstall,
    },
    license='license.txt',
    description='my test package',
    long_description='long one',
    use_2to3=True,
    

)
            
    

