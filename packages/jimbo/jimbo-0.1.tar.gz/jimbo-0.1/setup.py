import os
from setuptools import setup, find_packages

# with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
#     README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='jimbo',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='GNU General Public License v3.0',
    description='JIM protocol messenger',
    long_description='JIM protocol messenger with kivy- and qt- interface on client',
    author='Evgeny Shkryabin',
    author_email='evgenyshkryabin@gmail.com',
    keywords=['python', 'jim', 'socket', 'server', 'client'],
    classifiers=[],
    install_requires=['PyQT5', 'SQLAlchemy', 'pymongo', 'Kivy'],
    entry_points={
        'console_scripts': [
            'jimbo_server = jimbo.server_start:server_start',
            'jimbo_kivy = jimbo.kivy_start:kivy_start',
            'jimbo_qt = jimbo.client_start:client_start'
        ]
    },
)
