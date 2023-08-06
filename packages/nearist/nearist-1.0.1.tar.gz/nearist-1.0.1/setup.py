from setuptools import setup, find_packages

setup(name='nearist',
      version='1.0.1',
      description='Tools for Nearist hardware',
      long_description=open('README.md').read(),
      url='http://github.com/nearist/nearist',
      author='Nearist',
      author_email='nick.ryan@nearist.io',
      license='MIT',
      packages=find_packages(),
      install_requires=[
      'numpy',  
      'enum', 
      ]
      )
