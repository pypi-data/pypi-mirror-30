from setuptools import setup

setup(name='compute_gc',
      version='1.0',
      description='Compute GC content of DNA sequences',
      author='Eunkyung Kim',
      author_email='eunkyung@usc.edu',
      packages=['compute_gc'],
      install_requires=[
          'biopython',
      ],      
      zip_safe=False)