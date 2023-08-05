from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='GOldwasher',
      version='0.2.8',
      description='''Light wrapper for the R topGO package that produces
                      interactive GO enrichment html reports''',
      long_description=readme(),
      classifiers=[],
#        'Development Status :: 3 - Alpha',
#        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
#        'Programming Language :: Python :: 2.7',
#        'Operating System :: POSIX :: Linux',
#        'Topic :: Scientific/Engineering :: Bio-Informatics',
#      ],
      keywords='GOldwasher GO term enrichment visualization',
      url='http://github.com/hpsbastos/GOldwasher',
      author='hpbastos',
      author_email='hpb29@cam.ac.uk',
      license='GPLv3',
      packages=['GOldwasher'],
      install_requires=[
          'networkx',
          'jinja2',
          'numpy',
          'pandas',
          'matplotlib',
          'rpy2==2.7.9',
          'pydot',
          'graphviz'  
      ],
      scripts=['bin/goldpanner'],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      include_package_data=True,
      zip_safe=False)
