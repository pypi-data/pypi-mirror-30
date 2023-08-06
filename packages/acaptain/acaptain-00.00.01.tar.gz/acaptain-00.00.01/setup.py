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
    name='acaptain',
    version='00.00.01',
    author='Alectryon LLC',
    author_email='mbiedler@gmail.com',
    packages=['acaptain',],
    url='http://pypi.python.org/pypi/acaptain/',    
    entry_points = {
        'console_scripts': ['captain=acaptain.command_line:main','startcaptaindb=acaptain.command_line:dbstartup','startcaptainss=acaptain.command_line:ssstartup','startcaptainui=acaptain.command_line:uistartup'],
    },
    license='license.txt',
    description='Farm monitoring',
    long_description='Package provides a local database integration, arduino sensor handling, and a UI for remote access to sensors',
    use_2to3=True,
    

)
            
    

