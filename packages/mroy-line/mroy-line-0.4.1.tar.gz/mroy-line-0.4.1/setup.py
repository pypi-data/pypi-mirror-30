

from setuptools import setup, find_packages
from setuptools.command.install import install
from shutil import copyfile
import os

class MyInstall(install):

    def run(self):
        print(" ... ...............")
        h = os.getenv("HOME")
        if os.path.exists(os.path.join(h, ".oh-my-zsh")):
            if not os.path.exists(os.path.join(h, ".oh-my-zsh/plugins/zpython")):
                os.mkdir(os.path.join(h, ".oh-my-zsh/plugins/zpython"))
            copyfile("zpython/zpython.plugin.zsh", os.path.join(h, ".oh-my-zsh/plugins/zpython/zpython.plugin.zsh"))
        install.run(self)

setup(name='mroy-line',
    version='0.4.1',
    cmdclass={
        'install': MyInstall,
    },
    description='a simple way to use mongo db, let db like dict',
    url='https://github.com/Qingluan/.git',
    author='Froy_Qing',
    author_email='darkhackdevil@gmail.com',
    license='gnu3.0',
    zip_safe=False,
    packages=find_packages(),
    install_requires=['termcolor','dill', 'jedi'],
    entry_points={
        'console_scripts': ['rp=P.cmd:run']
    },
)
