from setuptools import setup,find_packages

setup(
   name='pyspeech',
   version='0.0.0',
   description='A python speech recognition framework',
   author='Xinjian Li',
   packages=find_packages(),
   author_email='lixinjian1217@gmail.com',
   install_requires=['scikit-learn', 'numpy'], #external packages as dependencies
)
