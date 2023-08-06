from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='suftware',
      version='0.13',
      description='Statistics Using Field Theory',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Mathematics',
      ],
      keywords='density estimation',
      url='http://github.com/jbkinney/suftware',
      author='Wei-Chia Chen, Ammar Tareen, Justin B. Kinney',
      author_email='jkinney@cshl.edu',
      license='MIT',
      packages=['suftware'],
      include_package_data=True,
      install_requires=[
          'scipy>=1.0.0',
          'numpy>=1.10.1',
          'matplotlib>=2.0.0',
          'pandas>=0.20.3',
      ],
      test_suite='nose.collector',
	  tests_require=['nose'],
      zip_safe=False)