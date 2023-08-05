from setuptools import setup, find_packages
with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(name='ttlab',
      version='0.42.0',
      description='Next generation analysis software',
      url='',
      author='Christopher Tiburski and Johan Tenghamn',
      author_email='info@ttlab.se',
      license='MIT',
      packages=find_packages(),
      install_requires=requirements,
      zip_safe=False)
