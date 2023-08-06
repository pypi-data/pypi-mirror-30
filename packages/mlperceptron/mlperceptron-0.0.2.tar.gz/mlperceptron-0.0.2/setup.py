from setuptools import find_packages
from distutils.core import setup

with open('README.rst') as file:
    long_description = file.read()

setup(name='mlperceptron',
      version='0.0.2',
      description='Python implementation of multilayer perceptron neural network from scratch.',
      install_requires=[
          'numpy==1.13.3',
          'scipy==0.19.1'
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.4'
      ],
      keywords=(
          'Neural Network NN neural network multilayer perceptron machine learning logistic classifier'),
      url='https://github.com/paulokuong/mlperceptron',
      author='Paulo Kuong',
      author_email='paulo.kuong@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      long_description=long_description)
