

from setuptools import setup, find_packages


setup(name='mroy-line',
    version='0.3',
    description='a simple way to use mongo db, let db like dict',
    url='https://github.com/Qingluan/.git',
    author='Froy_Qing',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=['termcolor','dill'],
    entry_points={
        'console_scripts': ['rp=P.cmd:run']
    },
)


