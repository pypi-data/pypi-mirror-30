
from setuptools import setup

setup(name='androidact', version='0.1',
        description='Android CLI Tools',
        url='https://github.com/bvdaakster/act',
        author='Bas van den Aakster',
        py_modules=['androidact'],
        entry_points={
            'console_scripts': [
                'act = androidact:main'
            ]
        },
        install_requires=['Pillow==5.0.0'])
