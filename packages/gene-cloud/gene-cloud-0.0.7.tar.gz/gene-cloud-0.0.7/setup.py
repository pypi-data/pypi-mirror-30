#!/usr/bin/env python3
import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    sys.exit("error: install setuptools")

if sys.version_info < (3, 5):
    raise Exception('utrme requires Python 3.5 or higher.')


setup(name='gene-cloud',
      version='0.0.7',
      description='An enhancer for PaperBlast',
      url='https://github.com/sradiouy/Gene-Cloud',
      author='Santiago Radio',
      author_email='sradio91@gmail.com',
      license='MIT',
      python_requires='>=3.5',      
      install_requires=['mygene','requires'],
      packages=['GeneCloud'],
      package_data={'GeneCloud': ['pic']},
      include_package_data=True,
      entry_points={'console_scripts': ['genecloud = GeneCloud.__main__:main']},
      keywords=['genecloud', 'paperblast', 'uniprot','wordcloud','gene ontology'],
      classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Environment :: Console",
		"Intended Audience :: Science/Research",
		"License :: OSI Approved :: MIT License",
		'Operating System :: Unix',
		"Natural Language :: English",
		"Programming Language :: Python :: 3",
		"Topic :: Scientific/Engineering :: Bio-Informatics"
	],
      )
