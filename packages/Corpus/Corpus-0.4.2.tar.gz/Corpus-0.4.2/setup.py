from setuptools import setup
def readme():
    with open('README.md') as f:
        return f.read()
		
setup(name='Corpus',
      version='0.4.2',
      description='A simple English dictionary for Python',
	  long_description='This can be used to check spelling of processed text for furthur use.',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Indexing',
		'Natural Language :: English',
		'Programming Language :: Python :: 2.7',
      ],
      keywords='dictionary spelling english linguistic',
      url='https://github.com/aneeshb413/Corpus',
      author='Aneesh Bhat',
      author_email='aneeshb413@gmail.com',
      license='MIT',
      packages=['Corpus'],test_suite='nose.collector',
	  tests_require=['nose'],
	  include_package_data=True,
      zip_safe=False)