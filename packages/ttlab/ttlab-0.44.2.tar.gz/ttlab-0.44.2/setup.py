from setuptools import setup, find_packages
with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(name='ttlab',
      version='0.44.2',
      description='Physics lab equipment analysis software',
      long_description='Easy to use import scripts for the most common physics equipments such as XPS, mass spectrometer, light spectrometers. Functions for the most typical analysis procedures.',
      url='',
      author='Christopher Tiburski and Johan Tenghamn',
      author_email='info@ttlab.se',
      license='MIT',
      packages=find_packages(),
      install_requires=requirements,
      keywords='XPS Cary5000 MassSpec Mass spectrometer Light spectrometer Insplorion Physics Analysis Pfeiffer Multipak Plasmonics Activation energy X0Reactor Plasmons',
      classifiers=['Development Status :: 4 - Beta','Programming Language :: Python :: 3.6','Intended Audience :: Science/Research','Topic :: Scientific/Engineering :: Physics'],
      zip_safe=False)
