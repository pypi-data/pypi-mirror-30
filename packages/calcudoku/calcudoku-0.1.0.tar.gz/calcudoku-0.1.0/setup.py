from setuptools import setup
import versioneer

setup(
    name='calcudoku',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=['calcudoku'],
    url='',
    license='',
    author='Daniel Zawada',
    author_email='',
    description='', install_requires=['numpy', 'matplotlib']
)
