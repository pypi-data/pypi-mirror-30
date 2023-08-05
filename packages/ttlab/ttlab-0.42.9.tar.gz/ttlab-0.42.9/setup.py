from setuptools import setup, find_packages
with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(name='ttlab',
      version='0.42.9',
      description='Next generation analysis software',
      long_description='Next generation analysis software for XPS, spectrometer and mass spectrometer. Utilizing jupyter notebooks and offline plotly figures.',
      url='',
      author='Christopher Tiburski and Johan Tenghamn',
      author_email='info@ttlab.se',
      license='MIT',
      packages=find_packages(),
      install_requires=requirements,
      keywords='XPS Cary5000 MassSpec',
      classifiers=['Development Status :: 4 - Beta','Programming Language :: Python :: 3.6','Intended Audience :: Science/Research','Topic :: Scientific/Engineering :: Physics'],
      zip_safe=False)
