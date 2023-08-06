from setuptools import setup, find_packages
from os.path import join, dirname
import src.version

setup(
    name='mlc-tools',
    version=src.__version__,
    packages=find_packages('src'),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
    ]
    # entry_points={
    #     'console_scripts':
    #         ['mlc-tools = src.main:console']
    # },
    # test_suite='tests'
)
