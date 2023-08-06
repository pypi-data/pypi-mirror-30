from setuptools import setup, find_packages
from factory_alchemist import __version__


setup(name='Factory-Alchemist',
      version=__version__,
      packages=find_packages(exclude=['*test*']),
      url='https://bitbucket.org/sievetech/factory-alchemist',
      author='Eduardo Matos',
      keywords='sql sqlalchemy modelmommy orm')
